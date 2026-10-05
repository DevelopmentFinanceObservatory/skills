"""Tests for scripts/validate_skills.py.

Runnable with a stock interpreter: ``python -m unittest discover``. Each rule
from the validator gets its own temporary skill directory, built fresh under
a TemporaryDirectory, so a test only proves what it claims to prove and
leaves nothing behind.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unicodedata
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_skills.py"

_spec = importlib.util.spec_from_file_location("validate_skills", SCRIPT_PATH)
validate_skills = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
sys.modules["validate_skills"] = validate_skills  # dataclass() needs this registered to resolve types
_spec.loader.exec_module(validate_skills)


def front_matter(name: str, description: str = "Covers a narrow test domain and when to load it.") -> str:
    return f"---\nname: {name}\ndescription: >-\n  {description}\n---\n"


EMPTY_ATTACHMENTS = "applies_to: []\nsources: []\n"


def make_skill(
    skills_root: Path,
    name: str,
    *,
    skill_md: str | None = None,
    body: str = "\n# Title\n\nSome body text.\n",
    references: dict[str, str] | None = None,
    loose_files: dict[str, str] | None = None,
    no_skill_md: bool = False,
    attachments: str | None = EMPTY_ATTACHMENTS,
) -> Path:
    """Create skills_root/<name>/ with the given contents and return its path.

    attachments is the text of the skill's attachments.yaml; None leaves the
    file out.
    """
    skill_dir = skills_root / name
    skill_dir.mkdir(parents=True)
    if not no_skill_md:
        content = skill_md if skill_md is not None else front_matter(name) + body
        (skill_dir / "SKILL.md").write_text(content)
    if attachments is not None:
        (skill_dir / "attachments.yaml").write_text(attachments)
    if references:
        ref_dir = skill_dir / "references"
        ref_dir.mkdir()
        for fname, content in references.items():
            (ref_dir / fname).write_text(content)
    if loose_files:
        for fname, content in loose_files.items():
            (skill_dir / fname).write_text(content)
    return skill_dir


def run(skills_root: Path, ontology_nodes: set[str] | None = None):
    """Return (findings, skill_count) from validate_repo."""
    return validate_skills.validate_repo(skills_root, ontology_nodes)


def run_main(skills_root: Path, *extra_args: str) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exit_code = validate_skills.main([str(skills_root), *extra_args])
    return exit_code, buf.getvalue()


def errors_with_rule(findings, rule: int):
    return [f for f in findings if f.level == "ERROR" and f.rule == rule]


def warnings_with_rule(findings, rule: int):
    return [f for f in findings if f.level == "WARNING" and f.rule == rule]


class ValidateSkillsTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp_path = Path(self._tmp.name)
        self.skills_root = self.tmp_path / "skills"
        self.skills_root.mkdir()

    # -- Rule 1: SKILL.md missing -----------------------------------------

    def test_rule1_missing_skill_md_is_an_error(self):
        make_skill(self.skills_root, "no-skill-md", no_skill_md=True)
        findings, count = run(self.skills_root)
        self.assertEqual(count, 1)
        hits = errors_with_rule(findings, 1)
        self.assertEqual(len(hits), 1)
        self.assertIn("missing", hits[0].message)
        exit_code, _ = run_main(self.skills_root)
        self.assertEqual(exit_code, 1)

    # -- Rule 2: malformed / absent / misplaced front matter ---------------

    def test_rule2_front_matter_anchor_or_alias(self):
        skill_md = "---\nname: anchored\ndescription: &d Covers a test domain.\nlicense: *d\n---\nBody.\n"
        make_skill(self.skills_root, "anchored", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 2)
        self.assertEqual(len(hits), 1)
        self.assertIn("anchors and aliases", hits[0].message)

    def test_rule2_no_front_matter_at_all(self):
        make_skill(self.skills_root, "no-front-matter", skill_md="# Just a heading\n\nNo front matter here.\n")
        findings, _ = run(self.skills_root)
        self.assertEqual(len(errors_with_rule(findings, 2)), 1)

    def test_rule2_front_matter_not_on_first_line(self):
        skill_md = "\n" + front_matter("late-front-matter") + "\nBody.\n"
        make_skill(self.skills_root, "late-front-matter", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        self.assertEqual(len(errors_with_rule(findings, 2)), 1)

    def test_rule2_front_matter_never_closed(self):
        skill_md = "---\nname: unclosed\ndescription: >-\n  Some text.\n\nBody without a closing marker.\n"
        make_skill(self.skills_root, "unclosed", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        self.assertEqual(len(errors_with_rule(findings, 2)), 1)

    def test_rule2_invalid_yaml_is_malformed(self):
        # An unterminated flow sequence is invalid YAML. The validator
        # reports it as an ordinary rule 2 error rather than crashing.
        skill_md = "---\nname: bad-yaml\ndescription: [unterminated\n---\n\nBody.\n"
        make_skill(self.skills_root, "bad-yaml", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        self.assertEqual(len(errors_with_rule(findings, 2)), 1)

    def test_rule2_front_matter_not_a_mapping_is_malformed(self):
        # A front matter block that parses as valid YAML but not as a
        # top-level mapping (here, a list) must also be a plain rule 2 error.
        skill_md = "---\n- one\n- two\n---\n\nBody.\n"
        make_skill(self.skills_root, "not-a-mapping", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 2)
        self.assertEqual(len(hits), 1)
        self.assertIn("mapping", hits[0].message)

    # -- Every YAML scalar form 'description' can take is accepted ------------
    # PyYAML's safe_load accepts every scalar form the spec permits for
    # 'description': plain, single- and double-quoted, and the folded and
    # literal block forms, including the spec's own canonical minimal
    # example. These tests lock that in.

    def test_spec_canonical_minimal_example_passes_with_zero_findings(self):
        skill_md = (
            "---\n"
            "name: skill-name\n"
            "description: A description of what this skill does and when to use it.\n"
            "---\n\nBody.\n"
        )
        make_skill(self.skills_root, "skill-name", skill_md=skill_md)
        findings, count = run(self.skills_root)
        self.assertEqual(count, 1)
        self.assertEqual(findings, [])

    def test_every_description_scalar_form_is_accepted(self):
        forms = {
            "plain": "description: A description of what this skill does and when to use it.",
            "single-quoted": "description: 'A description of what this skill does and when to use it.'",
            "double-quoted": 'description: "A description of what this skill does and when to use it."',
            "folded-clipped": "description: >\n  A description of what this skill does and when to use it.",
            "folded-stripped": "description: >-\n  A description of what this skill does and when to use it.",
            "literal-clipped": "description: |\n  A description of what this skill does and when to use it.",
            "literal-stripped": "description: |-\n  A description of what this skill does and when to use it.",
        }
        for label, description_line in forms.items():
            with self.subTest(form=label):
                skills_root = self.tmp_path / f"skills-{label}"
                skills_root.mkdir()
                skill_md = f"---\nname: form-skill\n{description_line}\n---\n\nBody.\n"
                make_skill(skills_root, "form-skill", skill_md=skill_md)
                findings, count = run(skills_root)
                self.assertEqual(count, 1)
                self.assertEqual(findings, [], f"{label} form produced findings: {findings}")

    # -- Rule 20: frontmatter scalar field has the wrong YAML type ------------

    def test_rule20_name_with_non_string_type_is_an_error_not_a_crash(self):
        # safe_load hands back an int for an unquoted numeric-looking name.
        # Rule 20 reports that instead of letting the validator crash later
        # when it calls .strip() on the value.
        skill_md = "---\nname: 123\ndescription: >-\n  Some description text.\n---\n\nBody.\n"
        make_skill(self.skills_root, "123", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 20)
        self.assertEqual(len(hits), 1)
        self.assertIn("name", hits[0].message)
        # name was neutralised to None rather than used, so rule 3 also fires
        # ("missing or empty") instead of crashing.
        self.assertEqual(len(errors_with_rule(findings, 3)), 1)

    def test_rule20_compatibility_with_non_string_type_is_an_error_not_a_crash(self):
        skill_md = "---\nname: bad-compat\ndescription: >-\n  Some description text.\ncompatibility: 3.11\n---\n\nBody.\n"
        make_skill(self.skills_root, "bad-compat", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 20)
        self.assertEqual(len(hits), 1)
        self.assertIn("compatibility", hits[0].message)
        # compatibility was neutralised to None, so rule 16's len() check
        # never runs against a float and never crashes.
        self.assertEqual(len(errors_with_rule(findings, 16)), 0)

    # -- Rule 3: name/description missing or empty -------------------------

    def test_rule3_name_missing(self):
        skill_md = "---\ndescription: >-\n  Some description text.\n---\n\nBody.\n"
        make_skill(self.skills_root, "name-missing", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 3)
        self.assertEqual(len(hits), 1)
        self.assertIn("name", hits[0].message)

    def test_rule3_description_empty(self):
        # description: >- with nothing indented under it is a syntactically
        # valid, empty block scalar -- rule 3 catches this, not the
        # front-matter parser.
        skill_md = "---\nname: description-empty\ndescription: >-\n---\n\nBody.\n"
        make_skill(self.skills_root, "description-empty", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 3)
        self.assertEqual(len(hits), 1)
        self.assertIn("description", hits[0].message)

    # -- Rule 4: name must match directory ----------------------------------

    def test_rule4_name_does_not_match_directory(self):
        make_skill(self.skills_root, "actual-dir-name", skill_md=front_matter("different-name") + "\nBody.\n")
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 4)
        self.assertEqual(len(hits), 1)
        self.assertIn("different-name", hits[0].message)
        self.assertIn("actual-dir-name", hits[0].message)

    def test_rule4_nfkc_normalization_treats_equivalent_unicode_forms_as_matching(self):
        # https://agentskills.io/specification#name-field: name "must match
        # the parent directory name". The same accented character can be
        # encoded as one precomposed code point (NFC) or a base letter plus a
        # combining mark (NFD); a directory and a front matter value holding
        # the same text in different forms must be treated as matching.
        nfc_name = unicodedata.normalize("NFC", "café-notes")
        nfd_dir_name = unicodedata.normalize("NFD", "café-notes")
        self.assertNotEqual(nfc_name, nfd_dir_name)  # different byte sequences, same text
        make_skill(self.skills_root, nfd_dir_name, skill_md=front_matter(nfc_name) + "\nBody.\n")
        findings, _ = run(self.skills_root)
        self.assertEqual(len(errors_with_rule(findings, 4)), 0)

    # -- Rule 5: name charset -------------------------------------------------

    def test_rule5_name_has_invalid_characters(self):
        make_skill(self.skills_root, "Invalid_Name", skill_md=front_matter("Invalid_Name") + "\nBody.\n")
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 5)
        self.assertEqual(len(hits), 1)
        # Same name on both sides, so rule 4 stays silent here.
        self.assertEqual(len(errors_with_rule(findings, 4)), 0)

    def test_rule5_name_has_doubled_hyphen(self):
        make_skill(self.skills_root, "oda--measures", skill_md=front_matter("oda--measures") + "\nBody.\n")
        findings, _ = run(self.skills_root)
        self.assertEqual(len(errors_with_rule(findings, 5)), 1)

    # -- Rule 6: name length ---------------------------------------------------

    def test_rule6_name_too_long(self):
        long_name = "a" * 65
        make_skill(self.skills_root, long_name, skill_md=front_matter(long_name) + "\nBody.\n")
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 6)
        self.assertEqual(len(hits), 1)
        # Valid charset and matches its directory, so rules 4 and 5 must be silent.
        self.assertEqual(len(errors_with_rule(findings, 4)), 0)
        self.assertEqual(len(errors_with_rule(findings, 5)), 0)

    # -- Rule 7: description length -------------------------------------------

    def test_rule7_description_too_long(self):
        long_description = "a" * 1100
        skill_md = front_matter("long-description", long_description) + "\nBody.\n"
        make_skill(self.skills_root, "long-description", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        self.assertEqual(len(errors_with_rule(findings, 7)), 1)

    # -- Rule 8: unknown front matter key --------------------------------------

    def test_rule8_unknown_front_matter_key(self):
        skill_md = (
            "---\nname: extra-key\ndescription: >-\n  Some description text.\nauthor: someone\n---\n\nBody.\n"
        )
        make_skill(self.skills_root, "extra-key", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 8)
        self.assertEqual(len(hits), 1)
        self.assertIn("author", hits[0].message)

    # -- Rule 15: spec-legal key outside what the README documents (warning) --

    def test_rule15_license_key_is_spec_legal_and_only_warns(self):
        # https://agentskills.io/specification#frontmatter lists 'license' as
        # a defined, optional field -- a skill using it is spec-compliant and
        # must not fail CI, even though README.md's "Format" section only
        # commits to 'name' and 'description'.
        skill_md = "---\nname: has-license\ndescription: >-\n  Some description text.\nlicense: MIT\n---\n\nBody.\n"
        make_skill(self.skills_root, "has-license", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        self.assertEqual(errors_with_rule(findings, 8), [])
        hits = warnings_with_rule(findings, 15)
        self.assertEqual(len(hits), 1)
        self.assertIn("license", hits[0].message)
        exit_code, _ = run_main(self.skills_root)
        self.assertEqual(exit_code, 0)  # a warning alone does not fail the build

    def test_rule15_fires_once_per_undocumented_spec_key(self):
        skill_md = (
            "---\nname: many-fields\ndescription: >-\n  Some description text.\n"
            "license: MIT\ncompatibility: Requires git.\nallowed-tools: Read\n---\n\nBody.\n"
        )
        make_skill(self.skills_root, "many-fields", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        self.assertEqual(errors_with_rule(findings, 8), [])
        hits = warnings_with_rule(findings, 15)
        self.assertEqual(len(hits), 3)
        self.assertEqual(
            {hit.message.split("'")[1] for hit in hits},
            {"license", "compatibility", "allowed-tools"},
        )

    # -- Rule 16: 'compatibility' length ---------------------------------------

    def test_rule16_compatibility_too_long_is_an_error(self):
        # https://agentskills.io/specification#compatibility-field: "Must be
        # 1-500 characters if provided".
        skill_md = (
            "---\nname: long-compat\ndescription: >-\n  Some description text.\n"
            f"compatibility: {'a' * 501}\n---\n\nBody.\n"
        )
        make_skill(self.skills_root, "long-compat", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        self.assertEqual(len(errors_with_rule(findings, 16)), 1)

    def test_rule16_compatibility_empty_is_an_error(self):
        skill_md = (
            "---\nname: empty-compat\ndescription: >-\n  Some description text.\n"
            "compatibility: \n---\n\nBody.\n"
        )
        make_skill(self.skills_root, "empty-compat", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        self.assertEqual(len(errors_with_rule(findings, 16)), 1)

    def test_rule16_compatibility_absent_is_fine(self):
        make_skill(self.skills_root, "no-compat")
        findings, _ = run(self.skills_root)
        self.assertEqual(errors_with_rule(findings, 16), [])

    # -- Rule 21: 'metadata' must be a map from string keys to string values --
    # safe_load hands back the real parsed type for 'metadata', so a value
    # like {tags: [oda, flows]} surfaces as a list rather than a string and
    # must be checked explicitly.

    def test_rule21_metadata_with_non_string_value_is_an_error(self):
        skill_md = (
            "---\nname: bad-metadata\ndescription: >-\n  Some description text.\n"
            "metadata: {tags: [oda, flows]}\n---\n\nBody.\n"
        )
        make_skill(self.skills_root, "bad-metadata", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 21)
        self.assertEqual(len(hits), 1)
        self.assertIn("tags", hits[0].message)

    def test_rule21_metadata_with_non_string_key_is_an_error(self):
        skill_md = (
            "---\nname: bad-metadata-key\ndescription: >-\n  Some description text.\n"
            "metadata: {123: oda}\n---\n\nBody.\n"
        )
        make_skill(self.skills_root, "bad-metadata-key", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        self.assertEqual(len(errors_with_rule(findings, 21)), 1)

    def test_rule21_metadata_that_is_not_a_mapping_is_an_error(self):
        skill_md = (
            "---\nname: scalar-metadata\ndescription: >-\n  Some description text.\n"
            "metadata: not a mapping\n---\n\nBody.\n"
        )
        make_skill(self.skills_root, "scalar-metadata", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        self.assertEqual(len(errors_with_rule(findings, 21)), 1)

    def test_rule21_metadata_with_all_string_values_is_fine(self):
        skill_md = (
            "---\nname: good-metadata\ndescription: >-\n  Some description text.\n"
            'metadata:\n  author: example-org\n  version: "1.0"\n---\n\nBody.\n'
        )
        make_skill(self.skills_root, "good-metadata", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        self.assertEqual(errors_with_rule(findings, 21), [])

    def test_allowed_tools_stays_a_space_separated_string_not_a_list(self):
        # allowed-tools is handled as the spec defines it: a plain
        # space-separated string, checked as a string rather than coerced
        # into a list.
        skill_md = (
            "---\nname: tools-skill\ndescription: >-\n  Some description text.\n"
            "allowed-tools: Bash(git:*) Read Grep\n---\n\nBody.\n"
        )
        make_skill(self.skills_root, "tools-skill", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        self.assertEqual(errors_with_rule(findings, 20), [])
        self.assertEqual(errors_with_rule(findings, 8), [])

    # -- Rules 17/18: no XML tags in name/description --------------------------

    def test_rule17_name_with_xml_tag_is_an_error(self):
        # https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#skill-structure
        # "'name': ... Cannot contain XML tags"
        skill_md = "---\nname: <bad>\ndescription: >-\n  Some description text.\n---\n\nBody.\n"
        make_skill(self.skills_root, "xml-name", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        self.assertEqual(len(errors_with_rule(findings, 17)), 1)

    def test_rule18_description_with_xml_tag_is_an_error(self):
        # Same source: "'description': ... Cannot contain XML tags"
        skill_md = (
            "---\nname: xml-description\ndescription: >-\n  Has a <system> tag embedded.\n---\n\nBody.\n"
        )
        make_skill(self.skills_root, "xml-description", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        self.assertEqual(len(errors_with_rule(findings, 18)), 1)

    # -- Rule 19: reserved words in name ----------------------------------------

    def test_rule19_name_with_reserved_word_is_an_error(self):
        # https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#skill-structure
        # "'name': ... Cannot contain reserved words: 'anthropic', 'claude'"
        make_skill(self.skills_root, "claude-helper", skill_md=front_matter("claude-helper") + "\nBody.\n")
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 19)
        self.assertEqual(len(hits), 1)
        self.assertIn("claude", hits[0].message)

    def test_rule19_name_with_anthropic_reserved_word_is_an_error(self):
        make_skill(self.skills_root, "anthropic-tools", skill_md=front_matter("anthropic-tools") + "\nBody.\n")
        findings, _ = run(self.skills_root)
        self.assertEqual(len(errors_with_rule(findings, 19)), 1)

    def test_rule19_name_without_reserved_word_is_fine(self):
        make_skill(self.skills_root, "pdf-processing")
        findings, _ = run(self.skills_root)
        self.assertEqual(errors_with_rule(findings, 19), [])

    # -- Rule 41: skill id reserved by the Skills API reader ----------------------

    def test_rule41_reserved_skill_id_is_an_error(self):
        make_skill(self.skills_root, "healthz")
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 41)
        self.assertEqual(len(hits), 1)
        self.assertIn("'healthz'", hits[0].message)

    def test_rule41_reserved_front_matter_name_is_an_error(self):
        make_skill(self.skills_root, "other", skill_md=front_matter("healthz") + "\nBody.\n")
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 41)
        self.assertEqual(len(hits), 1)
        self.assertIn("'healthz'", hits[0].message)

    def test_rule41_name_containing_a_reserved_id_is_fine(self):
        make_skill(self.skills_root, "healthz-guide")
        findings, _ = run(self.skills_root)
        self.assertEqual(errors_with_rule(findings, 41), [])

    # -- Rule 9: dangling pointer ------------------------------------------------

    def test_rule9_pointer_does_not_resolve(self):
        body = "\nSee [references/missing.md](references/missing.md) for details.\n"
        make_skill(self.skills_root, "dangling-pointer", body=body)
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 9)
        self.assertEqual(len(hits), 1)
        self.assertIn("references/missing.md", hits[0].message)

    def test_rule9_markdown_link_pointer_to_real_reference_file_resolves_cleanly(self):
        # A pointer written as an ordinary Markdown link is recognised the
        # same as a bare "references/..." token: here it names a file that
        # actually exists, so the pointer resolves and the file counts as
        # referenced, producing zero findings.
        make_skill(
            self.skills_root,
            "md-link-pointer",
            body="\nSee [the docs](references/foo.md) for details.\n",
            references={"foo.md": "# Foo\n\nSome content.\n"},
        )
        findings, _ = run(self.skills_root)
        self.assertEqual(findings, [])

    def test_rule9_markdown_link_pointer_that_does_not_exist_is_visible(self):
        # "[label](b.md)" is caught via rule 22, since "b.md" never resolves
        # inside this skill's references/ directory.
        make_skill(self.skills_root, "md-link-dangling", body="\nSee [the docs](b.md) for details.\n")
        findings, _ = run(self.skills_root)
        self.assertEqual(len(errors_with_rule(findings, 22)), 1)

    def test_out_of_scope_markdown_link_targets_are_not_reported(self):
        # External URLs, absolute paths, and anchor-only fragments are out of
        # scope for pointer checking and must never be reported.
        body = (
            "\nSee [external](https://example.com/x.md), [abs](/etc/x.md) "
            "and [anchor](#section) here.\n"
        )
        make_skill(self.skills_root, "out-of-scope-links", body=body)
        findings, _ = run(self.skills_root)
        self.assertEqual(findings, [])

    # -- Rule 22: pointer escapes the skill's references/ directory -----------

    def test_rule22_dotdot_pointer_that_lands_back_on_skill_md_is_an_error(self):
        # Resolving a pointer purely against the filesystem would let
        # "references/../SKILL.md" reach SKILL.md itself and mask a
        # genuinely orphaned reference file, so escaping references/ via '..'
        # is its own error, regardless of what the path lands on.
        body = "\nSee [references/../SKILL.md](references/../SKILL.md) for details.\n"
        make_skill(self.skills_root, "dotdot-pointer", body=body)
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 22)
        self.assertEqual(len(hits), 1)
        self.assertIn("references/../SKILL.md", hits[0].message)

    def test_rule22_nested_pointer_via_markdown_link_is_visible_to_rule12(self):
        # The same generalised extraction must also make a Markdown-link
        # pointer visible to the nested-reference-pointer rule.
        make_skill(
            self.skills_root,
            "nested-md-link",
            body="\nSee [references/a.md](references/a.md).\n",
            references={
                "a.md": "# A\n\nSee [more](b.md) here.\n",
                "b.md": "# B\n\nNothing further.\n",
            },
        )
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 12)
        self.assertEqual(len(hits), 1)
        self.assertTrue(hits[0].path.endswith("references/a.md"))
        self.assertIn("b.md", hits[0].message)

    # -- Rule 10: orphaned reference file -----------------------------------------

    def test_rule10_orphaned_reference_file(self):
        make_skill(
            self.skills_root,
            "orphan-reference",
            body="\nNo pointers here.\n",
            references={"orphan.md": "# Orphan\n\nNever pointed to.\n"},
        )
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 10)
        self.assertEqual(len(hits), 1)
        self.assertIn("references/orphan.md", hits[0].message)

    # -- Rule 11: loose markdown file --------------------------------------------

    def test_rule11_loose_markdown_file_beside_skill_md(self):
        make_skill(
            self.skills_root,
            "loose-markdown",
            loose_files={"notes.md": "# Notes\n\nShould live under references/.\n"},
        )
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 11)
        self.assertEqual(len(hits), 1)
        self.assertIn("notes.md", hits[0].path)

    # -- Rule 12: reference pointing at another reference --------------------------

    def test_rule12_reference_points_at_another_reference(self):
        make_skill(
            self.skills_root,
            "nested-pointer",
            body="\nSee [references/a.md](references/a.md) and [references/b.md](references/b.md).\n",
            references={
                "a.md": "# A\n\nSee references/b.md for more.\n",
                "b.md": "# B\n\nNothing further.\n",
            },
        )
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 12)
        self.assertEqual(len(hits), 1)
        self.assertTrue(hits[0].path.endswith("references/a.md"))
        self.assertIn("references/b.md", hits[0].message)

    # -- Rule 23: reference names another reference by bare filename -------------

    def test_rule23_reference_with_bare_filename_pointer_is_an_error(self):
        make_skill(
            self.skills_root,
            "bare-filename-pointer",
            body="\nSee [references/a.md](references/a.md).\n",
            references={"a.md": "# A\n\nSee grants-loans-psi.md for more.\n"},
        )
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 23)
        self.assertEqual(len(hits), 1)
        self.assertTrue(hits[0].path.endswith("references/a.md"))
        self.assertIn("grants-loans-psi.md", hits[0].message)

    def test_rule23_bare_filename_in_skill_md_body_does_not_error(self):
        # Rule 23 scans reference files only. The same bare ".md" token in a
        # SKILL.md body is a statement about another skill, not a pointer this
        # skill's reference layout must resolve, so it must stay silent here.
        make_skill(
            self.skills_root,
            "bare-filename-in-skill-md",
            body="\nSee grants-loans-psi.md for more.\nSee [references/a.md](references/a.md).\n",
            references={"a.md": "# A\n\nNothing further.\n"},
        )
        findings, _ = run(self.skills_root)
        self.assertEqual(errors_with_rule(findings, 23), [])

    def test_rule23_references_prefixed_pointer_triggers_rule12_not_rule23(self):
        # A "references/b.md" pointer inside a reference file is exactly the
        # case rule 12 already owns; rule 23 must not double-report it.
        make_skill(
            self.skills_root,
            "prefixed-pointer",
            body="\nSee [references/a.md](references/a.md) and [references/b.md](references/b.md).\n",
            references={
                "a.md": "# A\n\nSee references/b.md for more.\n",
                "b.md": "# B\n\nNothing further.\n",
            },
        )
        findings, _ = run(self.skills_root)
        self.assertEqual(len(errors_with_rule(findings, 12)), 1)
        self.assertEqual(errors_with_rule(findings, 23), [])

    # -- Rule 27: bare reference pointer in SKILL.md ----------------------------

    def test_rule27_bare_pointer_in_skill_md_is_an_error(self):
        # The bare token still resolves (no rule 9) and still counts as naming
        # the file (no rule 10); the only finding is the missing link.
        make_skill(
            self.skills_root,
            "bare-pointer",
            body="\nSee references/a.md for details.\n",
            references={"a.md": "# A\n\nNothing further.\n"},
        )
        findings, _ = run(self.skills_root)
        self.assertEqual([f.rule for f in findings], [27])
        self.assertTrue(findings[0].path.endswith("SKILL.md"))
        self.assertIn("references/a.md", findings[0].message)
        self.assertIn("[references/a.md](references/a.md)", findings[0].message)

    def test_rule27_link_labelled_with_its_path_passes(self):
        make_skill(
            self.skills_root,
            "link-pointer",
            body="\n## References\n\n- [references/a.md](references/a.md) — what a covers\n",
            references={"a.md": "# A\n\nNothing further.\n"},
        )
        findings, _ = run(self.skills_root)
        self.assertEqual(findings, [])

    def test_rule27_names_only_the_bare_pointers_on_a_mixed_line(self):
        make_skill(
            self.skills_root,
            "mixed-pointers",
            body="\nLoad [references/a.md](references/a.md), then references/b.md and references/b.md again.\n",
            references={"a.md": "# A\n\nNothing.\n", "b.md": "# B\n\nNothing.\n"},
        )
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 27)
        self.assertEqual(len(hits), 1)
        self.assertIn("references/b.md", hits[0].message)
        self.assertNotIn("references/a.md", hits[0].message)
        self.assertIn("references/b.md. Write", hits[0].message)

    def test_rule27_bare_pointer_in_code_span_is_an_error(self):
        # A code span renders as code, not a link, so it is still bare.
        make_skill(
            self.skills_root,
            "code-span-pointer",
            body="\nSee `references/a.md` for details.\n",
            references={"a.md": "# A\n\nNothing further.\n"},
        )
        findings, _ = run(self.skills_root)
        self.assertEqual([f.rule for f in findings], [27])

    def test_rule27_does_not_scan_reference_files(self):
        # A pointer inside a reference file is rule 12's case, whatever its syntax.
        make_skill(
            self.skills_root,
            "bare-in-reference",
            body="\nSee [references/a.md](references/a.md) and [references/b.md](references/b.md).\n",
            references={
                "a.md": "# A\n\nSee references/b.md for more.\n",
                "b.md": "# B\n\nNothing further.\n",
            },
        )
        findings, _ = run(self.skills_root)
        self.assertEqual([f.rule for f in findings], [12])

    # -- Rule 24: description with a line break -------------------------------

    def test_rule24_literal_block_description_with_line_break_is_an_error(self):
        # A '|' literal block scalar keeps the line break the source has;
        # dfo-pipelines publishes 'description' as a single-line value, so
        # the break would silently join the words on either side of it.
        skill_md = (
            "---\nname: literal-description\ndescription: |\n  First line.\n  Second line.\n---\n\nBody.\n"
        )
        make_skill(self.skills_root, "literal-description", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 24)
        self.assertEqual(len(hits), 1)
        self.assertIn("line break", hits[0].message)

    def test_rule24_folded_description_does_not_error(self):
        # A '>-' folded block scalar collapses its line breaks into spaces,
        # so it never contains "\n" or "\r" once parsed.
        make_skill(self.skills_root, "folded-description")
        findings, _ = run(self.skills_root)
        self.assertEqual(errors_with_rule(findings, 24), [])

    def test_rule24_single_line_description_does_not_error(self):
        skill_md = (
            "---\nname: plain-description\n"
            "description: A description of what this skill does and when to use it.\n---\n\nBody.\n"
        )
        make_skill(self.skills_root, "plain-description", skill_md=skill_md)
        findings, _ = run(self.skills_root)
        self.assertEqual(errors_with_rule(findings, 24), [])

    # -- Rule 25: reference file stem outside the skill name format -----------

    def test_rule25_reference_stem_with_uppercase_is_an_error(self):
        make_skill(
            self.skills_root,
            "bad-ref-case",
            body="\nSee [references/Foo.md](references/Foo.md).\n",
            references={"Foo.md": "# Foo\n\nSome content.\n"},
        )
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 25)
        self.assertEqual(len(hits), 1)
        self.assertIn("Foo", hits[0].message)

    def test_rule25_reference_stem_with_comma_is_an_error(self):
        make_skill(
            self.skills_root,
            "bad-ref-comma",
            body="\nSee [references/a,b.md](references/a,b.md).\n",
            references={"a,b.md": "# A B\n\nSome content.\n"},
        )
        findings, _ = run(self.skills_root)
        self.assertEqual(len(errors_with_rule(findings, 25)), 1)

    def test_rule25_reference_stem_with_dot_is_an_error(self):
        # "a.b.md" has stem "a.b" -- the embedded dot is outside NAME_RE.
        make_skill(
            self.skills_root,
            "bad-ref-dot",
            body="\nSee [references/a.b.md](references/a.b.md).\n",
            references={"a.b.md": "# A B\n\nSome content.\n"},
        )
        findings, _ = run(self.skills_root)
        self.assertEqual(len(errors_with_rule(findings, 25)), 1)

    def test_rule25_reference_stem_with_underscore_is_an_error(self):
        make_skill(
            self.skills_root,
            "bad-ref-underscore",
            body="\nSee [references/a_b.md](references/a_b.md).\n",
            references={"a_b.md": "# A B\n\nSome content.\n"},
        )
        findings, _ = run(self.skills_root)
        self.assertEqual(len(errors_with_rule(findings, 25)), 1)

    def test_rule25_compliant_hyphenated_stem_does_not_error(self):
        make_skill(
            self.skills_root,
            "good-ref-stem",
            body="\nSee [references/grants-loans-psi.md](references/grants-loans-psi.md).\n",
            references={"grants-loans-psi.md": "# Grants loans PSI\n\nSome content.\n"},
        )
        findings, _ = run(self.skills_root)
        self.assertEqual(errors_with_rule(findings, 25), [])

    # -- Rule 26: soft line break in skill or reference prose -----------------

    def test_rule26_wrapped_paragraph_in_skill_body_is_an_error(self):
        body = (
            "\nThis is a paragraph that continues\n"
            "on the next line without a blank line between them.\n"
        )
        make_skill(self.skills_root, "wrapped-paragraph", body=body)
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 26)
        self.assertEqual(len(hits), 1)
        self.assertIn("soft line break", hits[0].message)
        self.assertTrue(hits[0].path.endswith("SKILL.md"))

    def test_rule26_wrapped_list_item_continuation_is_an_error(self):
        body = (
            "\n- A list item whose second line\n"
            "  continues without its own marker.\n"
            "- Another item, on one line.\n"
        )
        make_skill(self.skills_root, "wrapped-list-item", body=body)
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 26)
        self.assertEqual(len(hits), 1)

    def test_rule26_one_line_paragraphs_lists_and_nested_lists_pass(self):
        body = (
            "\n## A heading\n\n"
            "A one-line paragraph on its own.\n\n"
            "Another one-line paragraph after a blank line.\n\n"
            "- A one-line list item.\n"
            "- Another one-line list item.\n"
            "  - A nested one-line list item.\n"
            "- Back to the top level.\n\n"
            "1. A numbered item.\n"
            "2. Another numbered item.\n"
        )
        make_skill(self.skills_root, "clean-prose", body=body)
        findings, _ = run(self.skills_root)
        self.assertEqual(errors_with_rule(findings, 26), [])

    def test_rule26_table_directly_after_a_paragraph_passes(self):
        body = "\nA paragraph right before a table.\n| a | b |\n|---|---|\n| 1 | 2 |\n"
        make_skill(self.skills_root, "table-after-paragraph", body=body)
        findings, _ = run(self.skills_root)
        self.assertEqual(errors_with_rule(findings, 26), [])

    def test_rule26_fenced_code_with_consecutive_lines_passes(self):
        # Two non-blank code lines back to back inside a fence are fenced
        # code, not a wrapped paragraph.
        body = "\nSee the example below.\n\n```python\nfirst_line = 1\nsecond_line = 2\n```\n"
        make_skill(self.skills_root, "fenced-code", body=body)
        findings, _ = run(self.skills_root)
        self.assertEqual(errors_with_rule(findings, 26), [])

    def test_rule26_two_space_hard_break_passes(self):
        # A trailing two-space hard break is the documented way to keep an
        # intended line break inside a paragraph.
        body = "\nFirst line of an intended break.  \nSecond line, kept apart on purpose.\n"
        make_skill(self.skills_root, "hard-break", body=body)
        findings, _ = run(self.skills_root)
        self.assertEqual(errors_with_rule(findings, 26), [])

    def test_rule26_wrapped_reference_file_errors_on_its_own_path(self):
        make_skill(
            self.skills_root,
            "wrapped-reference",
            body="\nSee [references/a.md](references/a.md).\n",
            references={"a.md": "# A\n\nA paragraph that continues\non the next line.\n"},
        )
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 26)
        self.assertEqual(len(hits), 1)
        self.assertTrue(hits[0].path.endswith("references/a.md"))

    def test_rule26_indented_code_block_with_consecutive_lines_passes(self):
        # Two non-blank lines indented 4+ spaces directly after a blank line
        # are an indented code block, not a wrapped paragraph.
        body = "\nSome paragraph.\n\n    first_line = 1\n    second_line = 2\n\nMore text.\n"
        make_skill(self.skills_root, "indented-code", body=body)
        findings, _ = run(self.skills_root)
        self.assertEqual(errors_with_rule(findings, 26), [])

    def test_rule26_wrapped_nested_list_item_continuation_is_still_an_error(self):
        # Indented, but directly after a list-item line rather than a blank
        # line, so this is a wrapped continuation, not an indented code
        # block, and rule 26 flags it.
        body = "\n- Top item\n  - Nested item that wraps\n    onto a second indented line.\n"
        make_skill(self.skills_root, "wrapped-nested-list-item", body=body)
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 26)
        self.assertEqual(len(hits), 1)

    def test_rule26_consecutive_link_reference_definitions_pass(self):
        body = "\nSome text.\n\n[a]: http://example.com/a\n[b]: http://example.com/b\n"
        make_skill(self.skills_root, "link-ref-defs", body=body)
        findings, _ = run(self.skills_root)
        self.assertEqual(errors_with_rule(findings, 26), [])

    def test_rule26_setext_heading_underlines_pass(self):
        # '===' (H1) and '---' (H2) directly after a text line are setext
        # heading underlines, not a wrapped continuation of the text above.
        body = "\nTitle Text\n===\n\nSubtitle Text\n---\n\nBody paragraph.\n"
        make_skill(self.skills_root, "setext-headings", body=body)
        findings, _ = run(self.skills_root)
        self.assertEqual(errors_with_rule(findings, 26), [])

    def test_rule26_reports_count_and_more_suffix_past_the_sample_size(self):
        body = "\n" + "\n".join(f"Line {i}." for i in range(8))
        make_skill(self.skills_root, "many-wraps", body=body)
        findings, _ = run(self.skills_root)
        hits = errors_with_rule(findings, 26)
        self.assertEqual(len(hits), 1)
        self.assertIn("7 soft line breaks", hits[0].message)
        self.assertIn("more", hits[0].message)

    # -- Rule 13: long reference file with no table of contents (warning) ----------

    def test_rule13_long_reference_without_toc_warns(self):
        # Each "Line N." sits on its own line with a blank line on either
        # side, so this fixture stays clear of rule 26 (soft line breaks)
        # while still trivially exceeding REFERENCE_LINE_WARN.
        long_reference = "# Long\n\nNo table of contents here.\n\n" + "\n\n".join(
            f"Line {i}." for i in range(120)
        )
        make_skill(
            self.skills_root,
            "long-reference",
            body="\nSee [references/long.md](references/long.md).\n",
            references={"long.md": long_reference},
        )
        findings, _ = run(self.skills_root)
        self.assertEqual(len(errors_with_rule(findings, 13)), 0)  # it's a warning, not an error
        hits = warnings_with_rule(findings, 13)
        self.assertEqual(len(hits), 1)
        exit_code, _ = run_main(self.skills_root)
        self.assertEqual(exit_code, 0)  # warnings alone do not fail the build

    def test_rule13_long_reference_with_toc_does_not_warn(self):
        long_reference = (
            "# Long\n\n## Table of contents\n\n- one\n- two\n\n"
            + "\n\n".join(f"Line {i}." for i in range(120))
        )
        make_skill(
            self.skills_root,
            "long-reference-with-toc",
            body="\nSee [references/long.md](references/long.md).\n",
            references={"long.md": long_reference},
        )
        findings, _ = run(self.skills_root)
        self.assertEqual(len(warnings_with_rule(findings, 13)), 0)

    # -- Rule 14: overlong SKILL.md body (warning) ----------------------------------

    def test_rule14_long_skill_body_warns(self):
        # Blank line between each line for the same reason as the rule 13
        # fixture above: this must exercise only rule 14, not rule 26.
        long_body = "\n" + "\n\n".join(f"Line {i} of the body." for i in range(510))
        make_skill(self.skills_root, "long-body", body=long_body)
        findings, _ = run(self.skills_root)
        hits = warnings_with_rule(findings, 14)
        self.assertEqual(len(hits), 1)
        exit_code, _ = run_main(self.skills_root)
        self.assertEqual(exit_code, 0)

    # -- _template exception ---------------------------------------------------------

    def test_template_directory_is_skipped_entirely(self):
        make_skill(
            self.skills_root,
            "_template",
            skill_md=front_matter("skill-template") + "\nBody.\n",
        )
        findings, count = run(self.skills_root)
        self.assertEqual(count, 0)
        self.assertEqual(findings, [])

    # -- Regression guard for the governing principle ---------------------------------
    # A skill using every field the spec defines, with valid values, must produce zero
    # errors -- the failure mode this validator exists to avoid is a skill doing
    # something the spec explicitly blesses and getting a red CI run for it.

    def test_all_six_spec_fields_with_valid_values_yields_zero_errors(self):
        skill_md = (
            "---\n"
            "name: full-fields\n"
            "description: >-\n"
            "  Covers a narrow test domain and when to load it.\n"
            "license: MIT\n"
            "compatibility: Requires Python 3.11+ and network access.\n"
            "metadata:\n"
            "  author: example-org\n"
            '  version: "1.0"\n'
            "allowed-tools: Bash(git:*) Read\n"
            "---\n\nBody.\n"
        )
        make_skill(self.skills_root, "full-fields", skill_md=skill_md)
        findings, count = run(self.skills_root)
        self.assertEqual(count, 1)
        errors = [f for f in findings if f.level == "ERROR"]
        self.assertEqual(errors, [], f"expected zero errors, got: {errors}")
        exit_code, _ = run_main(self.skills_root)
        self.assertEqual(exit_code, 0)

    # -- Output shape ------------------------------------------------------------------

    def test_output_prefixes_and_summary_line(self):
        make_skill(self.skills_root, "no-skill-md", no_skill_md=True)
        exit_code, output = run_main(self.skills_root)
        self.assertEqual(exit_code, 1)
        self.assertIn("ERROR: ", output)
        self.assertIn("1 skill checked, 1 error, 0 warnings", output)

    def test_clean_repo_exits_zero_with_plural_summary(self):
        make_skill(self.skills_root, "skill-one")
        make_skill(self.skills_root, "skill-two")
        exit_code, output = run_main(self.skills_root)
        self.assertEqual(exit_code, 0)
        self.assertIn("2 skills checked, 0 errors, 0 warnings", output)

    # -- Canary: the real repository must pass with zero errors -----------------------

    def test_real_repo_skills_directory_has_zero_errors(self):
        real_skills_root = REPO_ROOT / "skills"
        findings, count = run(real_skills_root)
        errors = [f for f in findings if f.level == "ERROR"]
        self.assertEqual(errors, [], f"the repo's real skills/ must have no errors, got: {errors}")
        # Guards against a validator that vacuously finds nothing. The count is
        # derived from the tree rather than frozen, so adding a skill does not
        # fail this test, while a validator that silently skips every directory
        # still does.
        expected = sorted(
            d.name
            for d in real_skills_root.iterdir()
            if d.is_dir() and not d.name.startswith("_")
        )
        self.assertGreater(len(expected), 0, "no skills found to validate")
        self.assertEqual(count, len(expected))

    def test_bare_reference_filenames_in_prose_are_not_pointers(self):
        # A skill can name another skill's reference files in prose (e.g.
        # "flow-types.md") without having a references/ directory of its own.
        # Those bare mentions are not pointers, so they must not raise a
        # rule 22 (or rule 9) false positive.
        skill = make_skill(
            self.skills_root,
            "prose-mentions",
            body="\n# Title\n\nThe measures skill holds flow-types.md and price-basis.md.\n",
        )
        self.assertFalse((skill / "references").is_dir())
        findings = validate_skills.validate_skill(skill, self.tmp_path)
        self.assertEqual(findings, [])


class AttachmentsTests(unittest.TestCase):
    """Rules 28 to 33: each skill's attachments.yaml."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.skills_root = Path(self._tmp.name) / "skills"
        self.skills_root.mkdir()

    def findings_for(self, attachments: str | None):
        make_skill(self.skills_root, "attached", attachments=attachments)
        findings, _ = run(self.skills_root)
        return findings

    def assert_single_error(self, attachments: str | None, rule: int, *fragments: str):
        findings = self.findings_for(attachments)
        self.assertEqual(
            [(f.rule, f.level) for f in findings], [(rule, "ERROR")], f"unexpected findings: {findings}"
        )
        self.assertEqual(findings[0].path, "skills/attached/attachments.yaml")
        for fragment in fragments:
            self.assertIn(fragment, findings[0].message)
        exit_code, _ = run_main(self.skills_root)
        self.assertEqual(exit_code, 1)

    # -- Accepted shapes -----------------------------------------------------------

    def test_both_keys_with_valid_entries_pass(self):
        attachments = (
            "applies_to:\n"
            "  # A rationale comment beside the dcid it justifies.\n"
            "  - dcid:CRSPurposeCode930\n"
            "  - dcid:country/PacificIslandsUS\n"
            "sources:\n"
            "  - dcid:provenance/OECDCreditorReportingSystem\n"
        )
        self.assertEqual(self.findings_for(attachments), [])

    def test_absent_keys_and_empty_files_pass(self):
        for label, attachments in {
            "empty file": "",
            "comments only": "# Attaches nowhere.\n",
            "empty mapping": "{}\n",
            "applies_to only": "applies_to:\n  - dcid:grantEquivalent\n",
            "sources only": "sources:\n  - dcid:provenance/ONEImputedMultilateralSectors\n",
        }.items():
            with self.subTest(label):
                skills_root = Path(self._tmp.name) / label.replace(" ", "-")
                make_skill(skills_root, "attached", attachments=attachments)
                findings, _ = run(skills_root)
                self.assertEqual(findings, [])

    # -- Rule 28: missing file ----------------------------------------------------

    def test_rule28_missing_file_is_an_error(self):
        self.assert_single_error(None, 28, "attachments.yaml is missing")

    # -- Rule 29: malformed file ------------------------------------------------------

    def test_rule29_invalid_yaml_is_an_error(self):
        self.assert_single_error("applies_to: [unterminated\n", 29, "malformed")

    def test_rule29_top_level_list_is_an_error(self):
        self.assert_single_error("- dcid:CRSPurposeCode930\n", 29, "mapping", "list")

    def test_rule29_anchor_is_an_error(self):
        attachments = "applies_to: &shared\n  - dcid:CRSPurposeCode930\nsources: []\n"
        self.assert_single_error(attachments, 29, "anchors and aliases")

    def test_rule29_alias_is_an_error(self):
        attachments = "applies_to: &shared []\nsources: *shared\n"
        self.assert_single_error(attachments, 29, "anchors and aliases")

    def test_rule29_repeated_key_is_an_error(self):
        # safe_load alone would keep only the second list and drop the first.
        attachments = "applies_to:\n  - dcid:CRSPurposeCode930\napplies_to:\n  - dcid:grantEquivalent\n"
        self.assert_single_error(attachments, 29, "key repeated: applies_to")

    # -- Rule 30: unknown key ------------------------------------------------------------

    def test_rule30_unknown_key_is_an_error(self):
        attachments = "applies_to: []\nsources: []\napplies-to: []\n"
        self.assert_single_error(attachments, 30, "'applies-to'", "applies_to, sources")

    # -- Rule 31: value not a list ---------------------------------------------------------

    def test_rule31_scalar_value_is_an_error(self):
        self.assert_single_error("applies_to: dcid:CRSPurposeCode930\n", 31, "'applies_to'", "got str")

    def test_rule31_null_value_is_an_error(self):
        self.assert_single_error("applies_to: []\nsources:\n", 31, "'sources'", "got null", "sources: []")

    # -- Rule 32: malformed entry ------------------------------------------------------

    def test_rule32_malformed_applies_to_entries_are_errors(self):
        for label, entry in {
            "no prefix": "CRSPurposeCode930",
            "empty token": '"dcid:"',
            "inner space": '"dcid:CRS PurposeCode930"',
            "comma": '"dcid:CRSPurposeCode930,dcid:CRSPurposeCode600"',
            "quote": "\"dcid:CRS'930\"",
            "integer": "930",
            "nested list": "[dcid:CRSPurposeCode930]",
        }.items():
            with self.subTest(label):
                skills_root = Path(self._tmp.name) / label.replace(" ", "-")
                make_skill(skills_root, "attached", attachments=f"applies_to:\n  - {entry}\n")
                findings, _ = run(skills_root)
                self.assertEqual([f.rule for f in findings], [32], f"unexpected findings: {findings}")
                self.assertIn("ontology reference", findings[0].message)

    def test_rule32_malformed_sources_entries_are_errors(self):
        for label, entry in {
            "ontology node": "dcid:CRSPurposeCode930",
            "no dcid prefix": "provenance/OECDCreditorReportingSystem",
            "empty token": "dcid:provenance/",
            "extra segment": "dcid:provenance/OECD/CreditorReportingSystem",
        }.items():
            with self.subTest(label):
                skills_root = Path(self._tmp.name) / label.replace(" ", "-")
                make_skill(skills_root, "attached", attachments=f"sources:\n  - {entry}\n")
                findings, _ = run(skills_root)
                self.assertEqual([f.rule for f in findings], [32], f"unexpected findings: {findings}")
                self.assertIn(repr(entry), findings[0].message)
                self.assertIn("provenance reference", findings[0].message)

    # -- Rule 33: duplicate entry --------------------------------------------------------

    def test_rule33_duplicate_entry_is_an_error(self):
        attachments = "applies_to:\n  - dcid:grantEquivalent\n  - dcid:CRSPurposeCode930\n  - dcid:grantEquivalent\n"
        self.assert_single_error(attachments, 33, "'applies_to'", "'dcid:grantEquivalent'", "more than once")

    def test_same_entry_in_both_keys_is_not_a_duplicate(self):
        # Rule 33 counts within one list. The same string cannot be valid in
        # both lists, so the only finding is rule 32's on 'sources'.
        attachments = "applies_to:\n  - dcid:grantEquivalent\nsources:\n  - dcid:grantEquivalent\n"
        self.assert_single_error(attachments, 32, "'sources'")

    # -- The template's scaffold -------------------------------------------------------

    def test_template_attachments_scaffold_is_valid(self):
        # validate_repo skips _template, so this is the only check on the copy
        # authors start from.
        template = REPO_ROOT / "skills" / "_template"
        self.assertTrue((template / "attachments.yaml").is_file())
        self.assertEqual(validate_skills.validate_attachments(template, REPO_ROOT), [])


class BundleTests(unittest.TestCase):
    """Rules 35 to 40: a skill directory's layout and limits, as dfo-pipelines exports it."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.skills_root = Path(self._tmp.name) / "skills"
        self.skills_root.mkdir()
        self.skill = make_skill(self.skills_root, "bundled")

    def write(self, relative: str, data: bytes | str):
        path = self.skill / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data if isinstance(data, bytes) else data.encode())
        return path

    def rules(self) -> list[tuple[int, str]]:
        findings, _ = run(self.skills_root)
        return sorted((f.rule, f.path) for f in findings if f.level == "ERROR")

    def test_a_clean_bundle_has_no_findings(self):
        self.write("SKILL.md", front_matter("bundled") + "\nSee [references/a.md](references/a.md).\n")
        self.write("references/sub-dir/b.md", "Text.\n")
        self.write("references/a.md", "Text.\n")
        findings, _ = run(self.skills_root)
        self.assertEqual([f.rule for f in findings if f.level == "ERROR"], [10])
        self.assertEqual(validate_skills.validate_bundle(self.skill, self.skills_root.parent), [])

    def test_rule35_file_outside_the_layout(self):
        self.write("notes.txt", "x")
        self.write("scripts/run.py", "x")
        self.assertEqual(
            self.rules(), [(35, "skills/bundled/notes.txt"), (35, "skills/bundled/scripts/run.py")]
        )

    def test_rule35_non_markdown_file_under_references(self):
        self.write("references/data.csv", "a,b\n")
        self.assertIn((35, "skills/bundled/references/data.csv"), self.rules())

    def test_rule35_uppercase_md_extension_under_references(self):
        self.write("references/a.MD", "Text.\n")
        self.assertIn((35, "skills/bundled/references/a.MD"), self.rules())

    def test_rule35_loose_markdown_is_left_to_rule_11(self):
        self.write("loose.md", "Text.\n")
        self.assertEqual(self.rules(), [(11, "skills/bundled/loose.md")])

    def test_rule35_symlink(self):
        (self.skill / "link.md").symlink_to(self.skill / "SKILL.md")
        self.assertIn((35, "skills/bundled/link.md"), self.rules())

    def test_rule36_file_over_the_byte_limit(self):
        limit = validate_skills.MAX_FILE_BYTES
        self.write("attachments.yaml", "# " + "a" * limit + "\n")
        self.assertEqual(self.rules(), [(36, "skills/bundled/attachments.yaml")])

    def test_rule36_file_at_the_byte_limit_passes(self):
        limit = validate_skills.MAX_FILE_BYTES
        self.write("attachments.yaml", "#" * (limit - 1) + "\n")
        self.assertEqual(self.rules(), [])

    def test_rule37_reference_that_is_not_utf8_is_named_without_a_crash(self):
        self.write("references/a.md", b"caf\xe9\n")
        self.assertEqual(self.rules(), [(37, "skills/bundled/references/a.md")])

    def test_rule37_skill_md_that_is_not_utf8(self):
        self.write("SKILL.md", b"---\nname: bundled\n---\ncaf\xe9\n")
        self.assertEqual(self.rules(), [(37, "skills/bundled/SKILL.md")])

    def test_rule37_attachments_yaml_that_is_not_utf8(self):
        self.write("attachments.yaml", b"applies_to: []  # caf\xe9\n")
        self.assertEqual(self.rules(), [(37, "skills/bundled/attachments.yaml")])
        exit_code, output = run_main(self.skills_root)
        self.assertEqual(exit_code, 1)
        self.assertIn("not valid UTF-8", output)

    def test_rule37_ignores_a_binary_file_the_pipeline_never_reads(self):
        self.write("image.png", b"\x89PNG\xff\xfe")
        self.assertEqual(self.rules(), [(35, "skills/bundled/image.png")])

    def test_rule38_more_references_than_the_limit(self):
        for number in range(validate_skills.MAX_REFERENCES + 1):
            self.write(f"references/r{number}.md", "Text.\n")
        errors = [f for f in run(self.skills_root)[0] if f.rule == 38]
        self.assertEqual([f.path for f in errors], ["skills/bundled/references"])
        self.assertIn("51 reference files", errors[0].message)

    def test_rule38_exactly_the_limit_passes(self):
        for number in range(validate_skills.MAX_REFERENCES):
            self.write(f"references/r{number}.md", "Text.\n")
        self.assertEqual([f for f in run(self.skills_root)[0] if f.rule == 38], [])

    def test_rule39_path_over_the_character_limit(self):
        long_directory = "a" * 200
        relative = f"references/{long_directory}/{long_directory}/{long_directory}/b.md"
        self.assertGreater(len(relative), validate_skills.MAX_PATH_CHARACTERS)
        self.write(relative, "Text.\n")
        self.assertIn((39, f"skills/bundled/{relative}"), self.rules())

    def test_rule40_reference_directory_outside_the_name_format(self):
        self.write("references/Sub_Dir/a.md", "Text.\n")
        self.assertIn((40, "skills/bundled/references/Sub_Dir/a.md"), self.rules())

    def test_rule40_hyphenated_directory_passes(self):
        self.write("references/sub-dir/a.md", "Text.\n")
        self.assertNotIn(40, [rule for rule, _ in self.rules()])


class OntologyCheckTests(unittest.TestCase):
    """Rule 34 and the --ontology-mcf option: 'applies_to' entries resolve in the ontology."""

    MCF = (
        "# bench: prod\n\n"
        "Node: dcid:CRSPurposeCode930\ntypeOf: dcid:Enum\nname: \"Refugees\"\n\n"
        "Node: dcid:country/PacificIslandsUS\ntypeOf: dcid:Country\n"
    )

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.skills_root = self.root / "skills"
        self.skills_root.mkdir()
        self.mcf = self.root / "dfo.mcf"
        self.mcf.write_text(self.MCF)

    def attach(self, attachments: str):
        make_skill(self.skills_root, "attached", attachments=attachments)

    def test_load_ontology_nodes_reads_node_lines_only(self):
        self.assertEqual(
            validate_skills.load_ontology_nodes(self.mcf),
            {"dcid:CRSPurposeCode930", "dcid:country/PacificIslandsUS"},
        )

    def test_known_nodes_pass(self):
        self.attach("applies_to:\n  - dcid:CRSPurposeCode930\n  - dcid:country/PacificIslandsUS\n")
        exit_code, _ = run_main(self.skills_root, "--ontology-mcf", str(self.mcf))
        self.assertEqual(exit_code, 0)

    def test_missing_node_fails_naming_it(self):
        self.attach("applies_to:\n  - dcid:CRSPurposeCode930\n  - dcid:NoSuchNode\n")
        exit_code, output = run_main(self.skills_root, "--ontology-mcf", str(self.mcf))
        self.assertEqual(exit_code, 1)
        self.assertIn("skills/attached/attachments.yaml", output)
        self.assertIn("'dcid:NoSuchNode' is not a node in the ontology", output)
        self.assertNotIn("CRSPurposeCode930'", output)

    def test_missing_node_is_one_rule_34_error(self):
        self.attach("applies_to:\n  - dcid:NoSuchNode\n")
        findings, _ = run(self.skills_root, validate_skills.load_ontology_nodes(self.mcf))
        self.assertEqual([(f.rule, f.level) for f in findings], [(34, "ERROR")])

    def test_sources_are_not_checked_against_the_ontology(self):
        self.attach("sources:\n  - dcid:provenance/OECDCreditorReportingSystem\n")
        exit_code, _ = run_main(self.skills_root, "--ontology-mcf", str(self.mcf))
        self.assertEqual(exit_code, 0)

    def test_malformed_entry_gets_only_the_shape_error(self):
        self.attach("applies_to:\n  - CRSPurposeCode930\n")
        findings, _ = run(self.skills_root, validate_skills.load_ontology_nodes(self.mcf))
        self.assertEqual([f.rule for f in findings], [32])

    def test_without_the_option_unknown_nodes_pass(self):
        self.attach("applies_to:\n  - dcid:NoSuchNode\n")
        exit_code, _ = run_main(self.skills_root)
        self.assertEqual(exit_code, 0)

    def test_unreadable_or_node_less_mcf_refuses(self):
        self.attach("applies_to: []\n")
        empty = self.root / "empty.mcf"
        empty.write_text("# bench: prod\n")
        for label, path in {"missing": self.root / "absent.mcf", "no nodes": empty}.items():
            with self.subTest(label):
                err = io.StringIO()
                with contextlib.redirect_stderr(err):
                    exit_code, _ = run_main(self.skills_root, "--ontology-mcf", str(path))
                self.assertEqual(exit_code, 1)
                self.assertIn("ERROR:", err.getvalue())


if __name__ == "__main__":
    unittest.main()
