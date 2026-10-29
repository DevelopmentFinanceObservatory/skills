#!/usr/bin/env python3
"""Validate the skill bundles under ``skills/`` and ``internal/skills/``
against the Agent Skills spec and this repository's own CONTRIBUTING.md.

Every rule this script enforces traces to one of three sources, cited inline
next to the rule that implements it:

- The generic Agent Skills specification: https://agentskills.io/specification
- Anthropic's Claude-specific requirements, which add constraints the generic
  spec omits: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
  and https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- This repository's own CONTRIBUTING.md, in particular its "Format" section, for
  rules the spec leaves to each project (reference pointers, loose markdown,
  each skill's ``attachments.yaml``, and ``skills/categories.yaml``).

The three-tier policy this script applies: **error** on anything the spec
forbids, or that CONTRIBUTING.md commits to and a skill breaks; **warn**
where a skill is spec-legal but departs from a convention CONTRIBUTING.md
states (a warning prints and exits zero); **allow silently** anything the spec
permits that CONTRIBUTING.md says nothing about. The goal is that a skill
author doing something the spec explicitly blesses never gets a red CI run for
it.

Front matter is parsed with PyYAML's ``yaml.safe_load``, so every scalar form
YAML defines -- plain, single-quoted, double-quoted, and the block forms
``>``, ``>-``, ``|``, ``|-`` -- is accepted for every string field, matching
what the spec actually permits. A front matter block that fails to parse as
YAML, or that parses to anything other than a top-level mapping, is reported
as an error naming the file; it never crashes the run and never passes
silently.

The repository holds skills under two roots, and every rule for a skill's
files applies under both. ``skills/`` holds the skills offered for install:
the plugin at the repository root loads every directory there. The sibling
``internal/skills/`` holds skills that are published to the knowledge graph
and the docs site and are not offered for install; a repository may have no
such directory. ``skills/categories.yaml`` lists the skills under ``skills/``
only.

``template/``, the scaffold authors copy, sits outside both roots and is not
validated as a skill.
"""

from __future__ import annotations

import argparse
import posixpath
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import yaml
from yaml.composer import ComposerError
from yaml.constructor import ConstructorError

# Charset for 'name': this repo restricts it to the ASCII subset of what the
# spec allows ("unicode lowercase alphanumeric characters ... and hyphens",
# https://agentskills.io/specification#name-field). Every ASCII-lowercase
# name this regex accepts is therefore also spec-legal; it just does not
# attempt to validate the full Unicode case-folding rules for non-ASCII
# letters, which none of this repo's skills use.
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# A bare "references/<something>.md" token, stopping at whitespace or the
# punctuation that would end a markdown link or inline code span. Matches only
# within a single line, so a pointer hard-wrapped across two lines in prose is
# left unrecognised. This is one of two pointer syntaxes
# gather_reference_pointers() recognises -- see MD_LINK_TARGET_RE for the
# other (Markdown link targets). A bare token still counts as a pointer for
# rules 9, 10 and 12, and rule 27 rejects one in SKILL.md.
REFERENCE_POINTER_RE = re.compile(r"references/[^\s`()\[\]]+?\.md\b")
# An ordinary inline Markdown link, "[label](target)". The target is
# resolved the same way a bare "references/..." token is -- see
# gather_reference_pointers() and _is_out_of_scope_link_target().
MD_LINK_TARGET_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
TOC_HEADING_RE = re.compile(r"^#{1,6}\s*(table of contents|contents|toc)\s*$", re.IGNORECASE)
# A bare "<name>.md" token in prose, used to catch a reference file that names
# another reference file by its bare filename instead of carrying the material
# inline or reaching it from SKILL.md -- see rule 23. The negative lookbehind
# keeps the regex off a markdown link target ("[label](b.md)", whose "b" is
# preceded by '(') and off a path-qualified form ("references/b.md", whose "b"
# is preceded by '/'); rule 12 and rule 22 handle those two cases
# respectively, leaving this regex to catch only the bare-filename case.
# The '-' is excluded as well so hyphenated filenames ("policy-marker-scoring.md")
# are not matched by an interior substring (e.g. "marker-scoring.md" inside a
# link target or "loans-psi.md" inside a path).
BARE_FILENAME_RE = re.compile(r"(?<![a-z0-9/(\-])\b[a-z0-9-]+\.md\b")
# A generic HTML/XML tag shape (<name ...>, </name>, <name/>), used to check
# Anthropic's "cannot contain XML tags" rule for 'name' and 'description':
# https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#skill-structure
XML_TAG_RE = re.compile(r"</?[A-Za-z][^<>]*/?>")
# A URI scheme prefix ("https:", "mailto:", ...), used to recognise a
# Markdown link target that points off the filesystem entirely.
URI_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
# The block-starting shapes rule 26 (soft line breaks) must recognise on a
# stripped line -- see find_soft_line_breaks() and _line_kind(). A fence line
# is either a ``` or ~~~ marker (opening, with an optional info string, or
# closing); a heading is 1-6 '#' followed by a space or end of line; a list
# marker is '-', '*', '+' or 'N.'/'N)' followed by a space; a horizontal rule
# is three or more of the same '-', '*' or '_' character, optionally
# space-separated, and nothing else; a link reference definition is
# '[label]: target', indented by up to three spaces the way a paragraph is
# allowed to be.
FENCE_LINE_RE = re.compile(r"^(```|~~~)")
HEADING_LINE_RE = re.compile(r"^#{1,6}(\s|$)")
LIST_MARKER_LINE_RE = re.compile(r"^([-*+]|\d+[.)])\s")
HR_LINE_RE = re.compile(r"^(-\s*){3,}$|^(\*\s*){3,}$|^(_\s*){3,}$")
LINK_REF_DEF_LINE_RE = re.compile(r"^\s{0,3}\[[^\]]+\]:\s")
# A setext heading underline ('===' for H1, '---' for H2) is recognised as
# one only when find_soft_line_breaks() sees it directly after a prose line --
# see its is_setext_underline pass. In isolation this shape is ambiguous
# ('---' alone is already a horizontal rule via HR_LINE_RE), so
# find_soft_line_breaks() checks this regex directly, outside _line_kind()'s
# normal dispatch.
SETEXT_UNDERLINE_RE = re.compile(r"^(=+|-+)$")
# How many of a file's soft-line-break line numbers to name in one finding --
# see find_soft_line_breaks().
SOFT_LINE_BREAK_SAMPLE = 5
# https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#skill-structure
# "'name': ... Cannot contain reserved words: 'anthropic', 'claude'"
RESERVED_NAME_WORDS = ("anthropic", "claude")
# The Skills API reader's literal routes take precedence over its {skill_id}
# route, so it drops a skill with one of these ids (dfo-apis skills_index.config).
RESERVED_SKILL_IDS = frozenset({"healthz"})
TOC_LOOKAHEAD_LINES = 20
REFERENCE_LINE_WARN = 100
SKILL_BODY_LINE_WARN = 500
# Field length limits, all from the spec's frontmatter table:
# https://agentskills.io/specification#frontmatter
NAME_MAX_LEN = 64
DESCRIPTION_MAX_LEN = 1024
COMPATIBILITY_MAX_LEN = 500
# The six frontmatter fields the Agent Skills spec defines:
# https://agentskills.io/specification#frontmatter
SPEC_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
# Of those six, the three CONTRIBUTING.md's "Format" section says do the work.
# A key outside SPEC_KEYS is an error (the spec doesn't define it); a key inside
# SPEC_KEYS but outside DOCUMENTED_KEYS is spec-legal but departs from what this
# repo's own docs commit to, so it is a warning rather than an error.
DOCUMENTED_KEYS = {"name", "description", "license"}
# The licence of every skill in this repository (an SPDX id), which each
# SKILL.md names in its own front matter (rule 54).
LICENSE_ID = "CC-BY-4.0"
# The frontmatter fields the spec defines as plain string scalars. 'metadata'
# is checked separately (it is a mapping, not a scalar); 'allowed-tools' is
# one of these -- the spec defines it as a single space-separated string, and
# this validator checks only that the value is a string, without parsing it
# into a list.
STRING_FIELDS = ("name", "description", "license", "compatibility", "allowed-tools")
REFERENCES_DIRNAME = "references"
# The limits dfo-pipelines enforces when it exports a skill bundle; a bundle
# over any of them fails the export, so the validator refuses it first.
MAX_FILE_BYTES = 256 * 1024
MAX_REFERENCES = 50
MAX_PATH_CHARACTERS = 512
# Each skill's graph attachments, read by dfo-pipelines and left out of the
# graph; CONTRIBUTING.md's "Graph attachments" section describes them. Each key maps to the pattern every entry
# in its list must match in full, and the shape named in the error when one
# does not. An 'applies_to' entry is an ontology reference, 'dcid:' followed
# by a token with no whitespace, quote or comma; a '/' is allowed because
# ontology dcids such as 'country/PacificIslandsUS' carry one. A 'sources'
# entry is the provenance node of a dfo-pipelines export, whose token has no
# '/'.
ATTACHMENTS_FILENAME = "attachments.yaml"
ATTACHMENT_KEYS = {
    "applies_to": (
        re.compile(r"dcid:[^\s\"',]+"),
        "an ontology reference such as 'dcid:CRSPurposeCode930'",
    ),
    "sources": (
        re.compile(r"dcid:provenance/[^\s\"',/]+"),
        "a provenance reference such as 'dcid:provenance/OECDCreditorReportingSystem'",
    ),
}
# The index that files every skill in skills/ under one category, read by
# dfo-docs to group the published skill pages; CONTRIBUTING.md's "Categories" section describes
# it. 'sources' and 'uncategorised' each hold a list of skill names, and
# 'domains' maps each domain's name to one.
CATEGORIES_FILENAME = "categories.yaml"
CATEGORY_LIST_KEYS = ("sources", "uncategorised")
CATEGORY_DOMAINS_KEY = "domains"
# The second skill root, relative to the directory that holds skills/.
INTERNAL_SKILLS_PATH = Path("internal") / "skills"
# The text of each rule several skills state word for word, one Markdown file
# per rule id, at the repository root. Some hosts load one skill at a time, so
# each skill carries its own copy of a shared rule, between an opening and a
# closing marker line that name the rule. scripts/sync_shared_rules.py writes
# the source text into every marked copy.
SHARED_RULES_DIRNAME = "shared-rules"
SHARED_MARKER_RE = re.compile(r"^<!-- (/?)shared:(\S*) -->$", re.MULTILINE)
# What happens to a directory whose name starts with '_' under each root, for
# rule 50's message. dfo-pipelines and dfo-docs both skip such a directory.
UNDERSCORE_CONSEQUENCE = {
    "installable": "the plugin at the repository root loads every directory there, so users would install it",
    "internal": "dfo-pipelines and dfo-docs skip it, so it would never be published",
}


class FrontMatterError(ValueError):
    """Raised when SKILL.md front matter isn't the shape this repo commits to."""


class YamlMappingError(ValueError):
    """Raised when attachments.yaml or categories.yaml cannot be read as a YAML mapping."""


class OntologyError(ValueError):
    """Raised when the ontology MCF cannot be read or declares no nodes."""


class _NoAnchorLoader(yaml.SafeLoader):
    """``yaml.SafeLoader`` that refuses anchors and aliases.

    dfo-pipelines refuses them in SKILL.md front matter and in
    attachments.yaml, so a file that uses one fails there.
    """

    def compose_node(self, parent, index):
        event = self.peek_event()
        if isinstance(event, yaml.AliasEvent) or getattr(event, "anchor", None) is not None:
            raise ComposerError(None, None, "YAML anchors and aliases are not allowed", event.start_mark)
        return super().compose_node(parent, index)


class _UniqueKeyLoader(_NoAnchorLoader):
    """``_NoAnchorLoader`` that also refuses repeated keys.

    A repeated key would load as its last value alone, silently dropping every
    earlier list.
    """

    def construct_mapping(self, node, deep=False):
        mapping = super().construct_mapping(node, deep=deep)
        if len(mapping) < len(node.value):
            keys = Counter(str(self.construct_object(key_node, deep=deep)) for key_node, _ in node.value)
            repeated = ", ".join(sorted(key for key, count in keys.items() if count > 1))
            raise ConstructorError(None, None, f"key repeated: {repeated}", node.start_mark)
        return mapping


@dataclass(frozen=True)
class Finding:
    rule: int
    level: str  # "ERROR" or "WARNING"
    path: str
    message: str

    def render(self) -> str:
        return f"{self.level}: {self.path}: {self.message}"


def parse_front_matter(text: str) -> tuple[dict, str]:
    """Parse SKILL.md's front matter with ``_NoAnchorLoader``.

    Returns (fields, body): fields is whatever ``yaml.safe_load`` returns for
    the front matter block, with its keys coerced to ``str`` (a mapping key
    is not required to be a string by YAML itself, but every key this
    validator compares against SPEC_KEYS is one, and this keeps a stray
    non-string key from crashing that comparison rather than being reported
    as an unknown key); body is everything after the closing '---' line.

    Raises FrontMatterError when the file cannot be validated at all: it
    does not open with '---' on line 1, it is never closed with a second
    '---' line, its front matter block is not valid YAML or uses an anchor or alias, or that YAML does
    not parse to a mapping at the top level (a scalar, a list, etc.). Each of
    these is a caller-visible ERROR naming the file, never a crash and never
    a silent pass -- see validate_skill's use of this function.
    """
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise FrontMatterError("front matter must open with '---' on the first line")

    end = None
    for i in range(1, len(lines)):
        if lines[i] == "---":
            end = i
            break
    if end is None:
        raise FrontMatterError("front matter is never closed with a second '---' line")

    fm_text = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1 :])

    try:
        fields = yaml.load(fm_text, Loader=_NoAnchorLoader)
    except yaml.YAMLError as exc:
        raise FrontMatterError(f"invalid YAML: {str(exc).replace(chr(10), ' ')}") from exc

    if fields is None:
        fields = {}
    if not isinstance(fields, dict):
        raise FrontMatterError(
            f"front matter must be a YAML mapping at the top level, got {type(fields).__name__}"
        )

    return {str(k): v for k, v in fields.items()}, body


def parse_yaml_mapping(text: str) -> dict:
    """Parse attachments.yaml or categories.yaml with ``_UniqueKeyLoader``.

    Returns the top-level mapping with its keys coerced to ``str``, the same
    way parse_front_matter does. An empty file, or one holding only comments,
    is an empty mapping: every key is optional.

    Raises YamlMappingError when the text is not valid YAML, uses an anchor,
    an alias or a repeated key, or parses to anything other than a mapping.
    """
    try:
        data = yaml.load(text, Loader=_UniqueKeyLoader)
    except yaml.MarkedYAMLError as exc:
        mark = exc.problem_mark
        where = f" at line {mark.line + 1}, column {mark.column + 1}" if mark else ""
        raise YamlMappingError(f"{exc.problem}{where}") from exc
    except yaml.YAMLError as exc:
        raise YamlMappingError(str(exc).replace(chr(10), " ")) from exc

    if data is None:
        return {}
    if not isinstance(data, dict):
        raise YamlMappingError(f"must be a YAML mapping at the top level, got {type(data).__name__}")
    return {str(k): v for k, v in data.items()}


def load_ontology_nodes(mcf_path: Path) -> set[str]:
    """Return every node declared in a compiled ontology MCF, as ``dcid:X`` references.

    Reads the ``Node: dcid:X`` lines that ``dfo-ontology compile`` writes. An
    unreadable file, or one with no such line, raises OntologyError so a wrong
    path cannot pass every attachment as resolved.
    """
    try:
        text = mcf_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise OntologyError(f"cannot read {mcf_path}: {exc}") from exc
    nodes = {
        line.removeprefix("Node: ").strip()
        for line in text.splitlines()
        if line.startswith("Node: dcid:")
    }
    if not nodes:
        raise OntologyError(f"{mcf_path} declares no 'Node: dcid:...' lines")
    return nodes


def validate_attachments(
    skill_dir: Path, repo_root: Path, ontology_nodes: set[str] | None = None
) -> list[Finding]:
    """Check a skill's attachments.yaml against CONTRIBUTING.md's "Graph attachments" section.

    With ``ontology_nodes``, also check that every 'applies_to' entry is one
    of them (rule 34). 'sources' entries name dfo-pipelines provenance nodes,
    which the ontology does not declare, so they are not checked.

    Rules 28 to 34, all errors: the file is missing (28); it is not valid
    YAML, uses an anchor, an alias or a repeated key, or is not a mapping
    (29); it holds a key outside ATTACHMENT_KEYS (30); a key's value is not a
    list (31); an entry is not a string of the shape its key requires (32);
    an entry appears twice in its list (33); an 'applies_to' entry is not a
    node of the ontology (34).
    """
    attachments = skill_dir / ATTACHMENTS_FILENAME
    path = attachments.relative_to(repo_root).as_posix()
    if not attachments.is_file():
        return [
            Finding(
                28,
                "ERROR",
                path,
                f"{ATTACHMENTS_FILENAME} is missing; every skill has one, with empty lists when "
                "it attaches nowhere (CONTRIBUTING.md 'Format')",
            )
        ]

    try:
        data = parse_yaml_mapping(attachments.read_text(encoding="utf-8"))
    except YamlMappingError as exc:
        return [Finding(29, "ERROR", path, f"{ATTACHMENTS_FILENAME} is malformed: {exc}")]

    findings: list[Finding] = []
    for key in sorted(k for k in data if k not in ATTACHMENT_KEYS):
        findings.append(
            Finding(30, "ERROR", path, f"key '{key}' is not one of {', '.join(ATTACHMENT_KEYS)}")
        )

    for key, (pattern, shape) in ATTACHMENT_KEYS.items():
        entries = data.get(key, [])
        if not isinstance(entries, list):
            got = "null" if entries is None else type(entries).__name__
            findings.append(
                Finding(
                    31,
                    "ERROR",
                    path,
                    f"'{key}' must be a list, got {got}; write '{key}: []' or leave the key out "
                    "when the list is empty",
                )
            )
            continue
        for entry in entries:
            if not isinstance(entry, str) or not pattern.fullmatch(entry):
                findings.append(Finding(32, "ERROR", path, f"'{key}' entry {entry!r} is not {shape}"))
        counts = Counter(entry for entry in entries if isinstance(entry, str))
        for entry in sorted(e for e, count in counts.items() if count > 1):
            findings.append(Finding(33, "ERROR", path, f"'{key}' lists {entry!r} more than once"))
        if key == "applies_to" and ontology_nodes is not None:
            for entry in entries:
                if isinstance(entry, str) and pattern.fullmatch(entry) and entry not in ontology_nodes:
                    findings.append(
                        Finding(34, "ERROR", path, f"'applies_to' entry {entry!r} is not a node in the ontology")
                    )

    return findings


def validate_categories(skills_root: Path, skill_names: list[str]) -> list[Finding]:
    """Check categories.yaml against CONTRIBUTING.md's "Categories" section.

    ``skill_names`` is every skill directory under ``skills_root``.

    Rules 42 to 49, all errors: the file is missing (42); it is not UTF-8 or
    valid YAML, uses an anchor, an alias or a repeated key, or is not a
    mapping (43); it holds a key outside 'sources', 'domains' and
    'uncategorised' (44); 'domains' is not a mapping, or a list of skills is
    not a list of strings (45); a domain's name is outside the skill name
    format (46); an entry names no skill directory (47); a skill is listed
    more than once (48); a skill directory is listed nowhere (49).
    """
    categories = skills_root / CATEGORIES_FILENAME
    path = categories.relative_to(skills_root.parent).as_posix()
    if not categories.is_file():
        return [
            Finding(
                42,
                "ERROR",
                path,
                f"{CATEGORIES_FILENAME} is missing; it lists every skill under 'sources', a domain "
                "or 'uncategorised' (CONTRIBUTING.md 'Categories')",
            )
        ]

    try:
        data = parse_yaml_mapping(categories.read_text(encoding="utf-8"))
    except (YamlMappingError, UnicodeDecodeError) as exc:
        return [Finding(43, "ERROR", path, f"{CATEGORIES_FILENAME} is malformed: {exc}")]

    findings: list[Finding] = []
    known_keys = (*CATEGORY_LIST_KEYS, CATEGORY_DOMAINS_KEY)
    for key in sorted(k for k in data if k not in known_keys):
        findings.append(Finding(44, "ERROR", path, f"key '{key}' is not one of {', '.join(known_keys)}"))

    domains = data.get(CATEGORY_DOMAINS_KEY, {})
    if not isinstance(domains, dict):
        got = "null" if domains is None else type(domains).__name__
        findings.append(
            Finding(
                45,
                "ERROR",
                path,
                f"'{CATEGORY_DOMAINS_KEY}' must map each domain to a list of skills, got {got}; "
                "leave the key out when there is no domain",
            )
        )
        domains = {}
    for domain in domains:
        if not NAME_RE.fullmatch(str(domain)):
            findings.append(
                Finding(
                    46,
                    "ERROR",
                    path,
                    f"domain '{domain}' must be lowercase letters, digits and single hyphens, with "
                    "no leading, trailing or doubled hyphen, matching the skill name format",
                )
            )

    lists = {f"'{key}'": data.get(key, []) for key in CATEGORY_LIST_KEYS}
    lists.update({f"domain '{domain}'": entries for domain, entries in domains.items()})
    listed: Counter[str] = Counter()
    for label, entries in lists.items():
        if not isinstance(entries, list):
            got = "null" if entries is None else type(entries).__name__
            findings.append(
                Finding(45, "ERROR", path, f"{label} must be a list of skills, got {got}; write '[]' when it is empty")
            )
            continue
        for entry in entries:
            if isinstance(entry, str):
                listed[entry] += 1
            else:
                findings.append(Finding(45, "ERROR", path, f"{label} entry {entry!r} is not a skill name"))

    for name in sorted(listed.keys() - set(skill_names)):
        findings.append(Finding(47, "ERROR", path, f"'{name}' is not a skill directory under {skills_root.name}/"))
    for name in sorted(name for name, count in listed.items() if count > 1):
        findings.append(
            Finding(48, "ERROR", path, f"'{name}' is listed {listed[name]} times; a skill sits in one category")
        )
    for name in sorted(set(skill_names) - listed.keys()):
        findings.append(
            Finding(
                49,
                "ERROR",
                path,
                f"skill '{name}' is not listed; add it under 'sources', a domain or 'uncategorised'",
            )
        )
    return findings


@dataclass(frozen=True)
class SharedBlock:
    """One marked copy of a shared rule: its id, its text stripped, and the
    offsets of the text between its two marker lines."""

    rule_id: str
    body: str
    start: int
    end: int


def parse_shared_blocks(text: str) -> tuple[list[SharedBlock], list[str]]:
    """The marked copies of shared rules in ``text``, and what is wrong with its
    markers: a block opened inside another, a closing marker that matches no
    open block, or a block left open. Parsing stops at the first such problem."""
    blocks: list[SharedBlock] = []
    opened: re.Match[str] | None = None
    for marker in SHARED_MARKER_RE.finditer(text):
        closing, rule_id = marker.group(1) == "/", marker.group(2)
        if not closing and opened is not None:
            return blocks, [f"opens shared rule '{rule_id}' inside shared rule '{opened.group(2)}'"]
        if not closing:
            opened = marker
        elif opened is None or opened.group(2) != rule_id:
            return blocks, [f"closes shared rule '{rule_id}', which no marker above opens"]
        else:
            body = text[opened.end() : marker.start()]
            blocks.append(SharedBlock(rule_id, body.strip(), opened.end(), marker.start()))
            opened = None
    if opened is not None:
        return blocks, [f"opens shared rule '{opened.group(2)}' and never closes it"]
    return blocks, []


def load_shared_sources(repo_root: Path) -> tuple[dict[str, str], list[Finding]]:
    """Each shared rule's text by id, read from shared-rules/<id>.md, and rule
    55 findings for that directory: it is a symlink, or holds a symlink, a file
    other than '<id>.md' with an id in the skill name format, a file that is
    not UTF-8, or an empty one. A repository without the directory shares no
    rules."""
    directory = repo_root / SHARED_RULES_DIRNAME
    if directory.is_symlink():
        return {}, [Finding(55, "ERROR", SHARED_RULES_DIRNAME, "is a symlink; it must be a real directory")]
    sources: dict[str, str] = {}
    findings: list[Finding] = []
    for entry in sorted(directory.iterdir()) if directory.is_dir() else []:
        shown = entry.relative_to(repo_root).as_posix()
        if entry.is_symlink() or not entry.is_file() or entry.suffix != ".md" or not NAME_RE.match(entry.stem):
            findings.append(
                Finding(55, "ERROR", shown, f"{SHARED_RULES_DIRNAME}/ holds one '<rule-id>.md' file per shared rule")
            )
            continue
        try:
            text = entry.read_text(encoding="utf-8").strip()
        except UnicodeDecodeError:
            findings.append(Finding(55, "ERROR", shown, "is not valid UTF-8"))
            continue
        if not text:
            findings.append(Finding(55, "ERROR", shown, "is empty"))
            continue
        sources[entry.stem] = text
    return sources, findings


def skill_markdown_files(skills_root: Path) -> list[Path]:
    """Every SKILL.md and references/*.md under ``skills_root`` and
    internal/skills/ beside it, reached through real directories only."""
    repo_root = skills_root.parent
    files: list[Path] = []
    for root in (skills_root, repo_root / INTERNAL_SKILLS_PATH):
        if _symlink_on_the_way(root, repo_root) is not None or not root.is_dir():
            continue
        for skill_dir in sorted(root.iterdir()):
            if skill_dir.is_symlink() or not skill_dir.is_dir() or skill_dir.name.startswith("_"):
                continue
            references = skill_dir / REFERENCES_DIRNAME
            candidates = [skill_dir / "SKILL.md"]
            if references.is_dir() and not references.is_symlink():
                candidates += sorted(references.glob("*.md"))
            files += (path for path in candidates if path.is_file() and not path.is_symlink())
    return files


def validate_shared_rules(skills_root: Path) -> list[Finding]:
    """Check every marked copy of a shared rule against its source.

    Rules 55 and 56, both errors: shared-rules/ is malformed
    (load_shared_sources), a skill file's markers are broken or name a rule
    with no source, or a source has no marked copy (55); a marked copy differs
    from its source (56). A skill file that is not UTF-8 is left to rule 37.
    """
    repo_root = skills_root.parent
    sources, findings = load_shared_sources(repo_root)
    used: set[str] = set()
    for path in skill_markdown_files(skills_root):
        shown = path.relative_to(repo_root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        blocks, problems = parse_shared_blocks(text)
        findings.extend(Finding(55, "ERROR", shown, problem) for problem in problems)
        for block in blocks:
            used.add(block.rule_id)
            source = f"{SHARED_RULES_DIRNAME}/{block.rule_id}.md"
            if block.rule_id not in sources:
                findings.append(
                    Finding(55, "ERROR", shown, f"marks shared rule '{block.rule_id}', and {source} does not exist")
                )
            elif block.body != sources[block.rule_id]:
                findings.append(
                    Finding(
                        56,
                        "ERROR",
                        shown,
                        f"its copy of shared rule '{block.rule_id}' differs from {source}. Edit the "
                        "source, then run python scripts/sync_shared_rules.py",
                    )
                )
    for rule_id in sorted(sources.keys() - used):
        findings.append(
            Finding(55, "ERROR", f"{SHARED_RULES_DIRNAME}/{rule_id}.md", "no skill holds a marked copy of this rule")
        )
    return findings


def _string_field(
    fields: dict, key: str, findings: list[Finding], path: str, *, null_as_empty: bool = False
) -> str | None:
    """Return fields[key] if it is a plain string, else None.

    A hand-written parser could only ever produce strings; a real YAML
    parser can hand back an int, a bool, a list, a nested mapping -- anything
    YAML can express -- for a field the spec defines as a plain string. This
    reports that mismatch as rule 20 and returns None so the caller's
    downstream string operations (len(), .strip(), regex matches) never
    crash on a non-string value.

    A key that is absent from `fields` entirely and a key present with a YAML
    null (a bare 'key:' with nothing after it) both come back as None from
    this function's perspective; null_as_empty distinguishes them for a
    caller that -- like the 'compatibility' length check -- must treat
    "absent" as fine but "present with nothing in it" as an error. When set,
    a present null is returned as "" instead of None.
    """
    if key not in fields:
        return None
    value = fields[key]
    if value is None:
        return "" if null_as_empty else None
    if isinstance(value, str):
        return value
    findings.append(
        Finding(
            20,
            "ERROR",
            path,
            f"front matter '{key}' must be a plain YAML string, got {type(value).__name__}",
        )
    )
    return None


def _is_out_of_scope_link_target(target: str) -> bool:
    """True for a Markdown link target this validator must not resolve.

    External URLs ("https://..."), absolute paths ("/foo"), and anchor-only
    fragments ("#section") are all out of scope for reference-pointer
    checking -- see gather_reference_pointers().
    """
    return bool(target == "" or target.startswith("#") or target.startswith("/") or URI_SCHEME_RE.match(target))


def gather_reference_pointers(text: str) -> set[str]:
    """Collect every reference pointer named in `text`.

    Recognises two syntaxes: a bare "references/<name>.md" token in prose,
    and a Markdown link target, "[label](target)". A link target that is an
    external URL, an absolute path, or an anchor-only fragment is skipped (it
    is not a pointer into this skill's own files); a link target carrying a
    "#fragment" suffix has the fragment stripped before the remaining path is
    treated as a pointer.
    """
    pointers = set(REFERENCE_POINTER_RE.findall(text))
    for match in MD_LINK_TARGET_RE.finditer(text):
        target = match.group(1).strip()
        if _is_out_of_scope_link_target(target):
            continue
        target = target.split("#", 1)[0]
        if target:
            pointers.add(target)
    return pointers


def find_bare_reference_pointers(text: str) -> list[str]:
    """Return every "references/<name>.md" token in `text` that sits outside
    a Markdown link, sorted and without duplicates -- see rule 27.

    Every "[label](target)" is removed first, label and target together, so
    a link whose label repeats its target ("[references/a.md](references/a.md)")
    leaves nothing behind. A token in a code span or a reference-style link
    definition is still bare: neither renders as a link.
    """
    return sorted(set(REFERENCE_POINTER_RE.findall(MD_LINK_TARGET_RE.sub("", text))))


def _has_toc(lines: list[str]) -> bool:
    return any(TOC_HEADING_RE.match(line.strip()) for line in lines[:TOC_LOOKAHEAD_LINES])


def _plural(n: int, singular: str) -> str:
    return f"{n} {singular}" if n == 1 else f"{n} {singular}s"


def _line_kind(stripped: str) -> str:
    """Classify one already-stripped, non-blank line for find_soft_line_breaks().

    Returns one of the block shapes rule 26 treats specially: a fence marker,
    a heading, a table row, a list marker, a blockquote, an HTML tag, a
    horizontal rule, or a link reference definition, and "prose" for anything
    else. A setext heading underline is classified only in context, directly
    after a prose line, so find_soft_line_breaks() recognises it separately
    from this function.
    """
    if FENCE_LINE_RE.match(stripped):
        return "fence"
    if HEADING_LINE_RE.match(stripped):
        return "heading"
    if stripped.startswith("|"):
        return "table"
    if LIST_MARKER_LINE_RE.match(stripped):
        return "list"
    if stripped.startswith(">"):
        return "blockquote"
    if stripped.startswith("<"):
        return "html"
    if HR_LINE_RE.match(stripped):
        return "hr"
    if LINK_REF_DEF_LINE_RE.match(stripped):
        return "link_def"
    return "prose"


def _has_hard_break(line: str) -> bool:
    """True for a line ending in a Markdown hard break: two-plus trailing
    spaces, or a trailing backslash -- the way to keep an intended line break
    inside a paragraph. See find_soft_line_breaks()."""
    if line.endswith("\\"):
        return True
    return len(line) - len(line.rstrip(" ")) >= 2


def find_soft_line_breaks(text: str) -> list[int]:
    """Return the 1-indexed line numbers (counting front matter) of every
    soft line break in `text` -- see rule 26 in validate_skill().

    A soft line break is a non-blank line that is a continuation of the
    non-blank line before it: neither line sits inside a fenced code block
    (``` or ~~~, open to matching close), an indented code block (4+ spaces
    of indentation, starting directly after a blank line -- a wrapped list
    item continuation is indented but directly follows a list-item line
    instead, so it stays in scope), or the front matter block (a '---' line
    at position 1, to the next '---' line); the current line, stripped of
    indentation, does not start a new block (heading, list item, table row,
    fence, blockquote, HTML tag, horizontal rule, or link reference
    definition); the current and previous line are not a setext heading
    underline directly after the prose line it underlines; and the previous
    line is not itself a heading, table row or fence line, and does not end
    in a hard break.
    """
    lines = text.splitlines()
    n = len(lines)
    skip = [False] * n

    if n and lines[0] == "---":
        for i in range(1, n):
            if lines[i] == "---":
                for j in range(i + 1):
                    skip[j] = True
                break

    in_fence = False
    for i in range(n):
        if skip[i]:
            continue
        if FENCE_LINE_RE.match(lines[i].strip()):
            skip[i] = True
            in_fence = not in_fence
        elif in_fence:
            skip[i] = True

    in_indented_code = False
    for i in range(n):
        if skip[i]:
            in_indented_code = False
            continue
        if lines[i].strip() == "":
            continue
        indent = len(lines[i]) - len(lines[i].lstrip(" "))
        if in_indented_code:
            if indent >= 4:
                skip[i] = True
                continue
            in_indented_code = False
        elif indent >= 4 and i > 0 and not skip[i - 1] and lines[i - 1].strip() == "":
            skip[i] = True
            in_indented_code = True

    is_setext_underline = [False] * n
    for i in range(1, n):
        if skip[i] or skip[i - 1]:
            continue
        prev_stripped = lines[i - 1].strip()
        cur_stripped = lines[i].strip()
        if prev_stripped and SETEXT_UNDERLINE_RE.match(cur_stripped) and _line_kind(prev_stripped) == "prose":
            is_setext_underline[i] = True

    breaks: list[int] = []
    for i in range(1, n):
        if skip[i] or skip[i - 1]:
            continue
        prev_stripped = lines[i - 1].strip()
        cur_stripped = lines[i].strip()
        if prev_stripped == "" or cur_stripped == "":
            continue
        if is_setext_underline[i]:
            continue
        if _line_kind(cur_stripped) != "prose":
            continue
        if _line_kind(prev_stripped) in ("heading", "table", "fence") or is_setext_underline[i - 1]:
            continue
        if _has_hard_break(lines[i - 1]):
            continue
        breaks.append(i + 1)
    return breaks


def _soft_line_break_message(lines: list[int]) -> str:
    sample = lines[:SOFT_LINE_BREAK_SAMPLE]
    sample_str = ", ".join(str(n) for n in sample)
    remainder = len(lines) - len(sample)
    more = f" and {remainder} more" if remainder > 0 else ""
    return (
        f"{_plural(len(lines), 'soft line break')} (line{'s' if len(sample) != 1 else ''} "
        f"{sample_str}{more}): put each paragraph and each list item on one line, with a "
        "blank line between paragraphs; dfo-pipelines publishes this text to the knowledge "
        "graph, which drops line breaks and joins the words on either side of one"
    )


def validate_skill(skill_dir: Path, repo_root: Path) -> list[Finding]:
    """Check one skill's SKILL.md: its front matter, its body, and the files it points at.

    Rule 54, an error: front matter 'license' is missing or is not LICENSE_ID.
    A skill downloaded on its own travels without the repository's LICENSE, so
    each skill names the licence itself.
    """
    findings: list[Finding] = []

    def rel(p: Path) -> str:
        return p.relative_to(repo_root).as_posix()

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        findings.append(Finding(1, "ERROR", rel(skill_dir), "SKILL.md is missing"))
        return findings

    text = skill_md.read_text(encoding="utf-8")
    try:
        fields, body = parse_front_matter(text)
    except FrontMatterError as exc:
        findings.append(Finding(2, "ERROR", rel(skill_md), f"front matter is malformed: {exc}"))
        return findings

    # Rule 8 (ERROR): https://agentskills.io/specification#frontmatter defines
    # exactly six frontmatter fields. A key outside that set is not part of
    # the spec at all, so it errors regardless of what CONTRIBUTING.md says.
    unknown_keys = sorted(k for k in fields if k not in SPEC_KEYS)
    for key in unknown_keys:
        findings.append(
            Finding(
                8,
                "ERROR",
                rel(skill_md),
                f"front matter key '{key}' is not part of the Agent Skills spec "
                "(name, description, license, compatibility, metadata, allowed-tools)",
            )
        )

    # Rule 15 (WARNING): a key the spec allows but that CONTRIBUTING.md's "Format"
    # section doesn't mention -- spec-legal, repo-convention departure. This
    # is the case the governing principle exists for: a skill using something
    # the spec blesses must not fail CI for it.
    undocumented_keys = sorted(k for k in fields if k in SPEC_KEYS and k not in DOCUMENTED_KEYS)
    for key in undocumented_keys:
        findings.append(
            Finding(
                15,
                "WARNING",
                rel(skill_md),
                f"front matter key '{key}' is allowed by the Agent Skills spec, but CONTRIBUTING.md's "
                "'Format' section documents only 'name', 'description' and 'license'",
            )
        )

    # Rule 20 (ERROR): every field the spec defines as a plain string scalar
    # must actually be one -- see _string_field's docstring. 'license' and
    # 'allowed-tools' are checked for this alongside 'name', 'description'
    # and 'compatibility' even though nothing downstream reads their value,
    # so a skill author gets one clear error rather than a wrong type
    # quietly surviving because this script never happened to look at it.
    name = _string_field(fields, "name", findings, rel(skill_md))
    description = _string_field(fields, "description", findings, rel(skill_md))
    compatibility = _string_field(fields, "compatibility", findings, rel(skill_md), null_as_empty=True)
    _string_field(fields, "license", findings, rel(skill_md))
    _string_field(fields, "allowed-tools", findings, rel(skill_md))

    # Rule 54 (ERROR): see the docstring. A non-string value differs from
    # LICENSE_ID too, beside rule 20.
    if fields.get("license") != LICENSE_ID:
        findings.append(
            Finding(
                54,
                "ERROR",
                rel(skill_md),
                f"front matter 'license' is missing or is not '{LICENSE_ID}'; a skill downloaded on its own "
                "travels without the repository's LICENSE, so each skill names the licence itself",
            )
        )

    if not name or not name.strip():
        findings.append(Finding(3, "ERROR", rel(skill_md), "front matter 'name' is missing or empty"))
        name = None
    if not description or not description.strip():
        findings.append(Finding(3, "ERROR", rel(skill_md), "front matter 'description' is missing or empty"))
        description = None

    if name is not None:
        # Rule 4: https://agentskills.io/specification#name-field, "Must
        # match the parent directory name". The spec also allows "unicode
        # lowercase alphanumeric characters" in 'name', and the same
        # character can have more than one Unicode encoding (e.g. an accented
        # letter as one precomposed code point vs. a base letter plus a
        # combining mark) -- macOS in particular normalises filenames to one
        # of these forms on write. NFKC-normalising both sides before
        # comparing is the standard way to compare Unicode identifiers for
        # equivalence, so a name and directory that are the same text in
        # different Unicode forms are not flagged as a mismatch.
        if unicodedata.normalize("NFKC", name) != unicodedata.normalize("NFKC", skill_dir.name):
            findings.append(
                Finding(
                    4,
                    "ERROR",
                    rel(skill_md),
                    f"front matter name '{name}' does not match its directory name '{skill_dir.name}'",
                )
            )
        if not NAME_RE.match(name):
            findings.append(
                Finding(
                    5,
                    "ERROR",
                    rel(skill_md),
                    f"front matter name '{name}' must be lowercase letters, digits and single "
                    "hyphens, with no leading, trailing or doubled hyphen",
                )
            )
        if len(name) > NAME_MAX_LEN:
            findings.append(
                Finding(
                    6,
                    "ERROR",
                    rel(skill_md),
                    f"front matter name is {len(name)} characters, longer than the {NAME_MAX_LEN}-character limit",
                )
            )
        # Rule 17 (ERROR): https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#skill-structure
        # "'name': ... Cannot contain XML tags"
        if XML_TAG_RE.search(name):
            findings.append(
                Finding(17, "ERROR", rel(skill_md), f"front matter name '{name}' must not contain XML tags")
            )
        # Rule 19 (ERROR): same source, "Cannot contain reserved words:
        # 'anthropic', 'claude'".
        lowered_name = name.lower()
        reserved_hits = [w for w in RESERVED_NAME_WORDS if w in lowered_name]
        if reserved_hits:
            findings.append(
                Finding(
                    19,
                    "ERROR",
                    rel(skill_md),
                    f"front matter name '{name}' must not contain the reserved word "
                    f"{'/'.join(reserved_hits)!r}",
                )
            )

    # Rule 41 (ERROR): an exact-match id the Skills API reader reserves, taken
    # from the directory name or the front matter name.
    for reserved_id in sorted({skill_dir.name, name} & RESERVED_SKILL_IDS):
        findings.append(
            Finding(
                41,
                "ERROR",
                rel(skill_md),
                f"skill id '{reserved_id}' is reserved by the Skills API reader, which drops a skill "
                "with that id from the catalogue",
            )
        )

    if description is not None:
        if len(description) > DESCRIPTION_MAX_LEN:
            findings.append(
                Finding(
                    7,
                    "ERROR",
                    rel(skill_md),
                    f"front matter description is {len(description)} characters, longer than the "
                    f"{DESCRIPTION_MAX_LEN}-character limit",
                )
            )
        # Rule 18 (ERROR): https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#skill-structure
        # "'description': ... Cannot contain XML tags"
        if XML_TAG_RE.search(description):
            findings.append(
                Finding(18, "ERROR", rel(skill_md), "front matter description must not contain XML tags")
            )
        # Rule 24 (ERROR): dfo-pipelines publishes 'description' into the
        # knowledge graph as a single-line value, so a line break in the
        # parsed string is dropped rather than kept, joining the words on
        # either side of it. A '|' or '|-' literal block scalar introduces
        # one for every line break in the source; a folded '>-' scalar (or a
        # plain single-line value) does not.
        if "\n" in description or "\r" in description:
            findings.append(
                Finding(
                    24,
                    "ERROR",
                    rel(skill_md),
                    "front matter description contains a line break; use a folded '>-' block "
                    "or a single line (dfo-pipelines publishes it as one line)",
                )
            )

    # Rule 16 (ERROR): https://agentskills.io/specification#compatibility-field
    # "Must be 1-500 characters if provided". Absent is fine (optional field);
    # present-but-empty or over-length is not.
    if compatibility is not None and not (1 <= len(compatibility) <= COMPATIBILITY_MAX_LEN):
        findings.append(
            Finding(
                16,
                "ERROR",
                rel(skill_md),
                f"front matter 'compatibility' is {len(compatibility)} characters, must be between "
                f"1 and {COMPATIBILITY_MAX_LEN}",
            )
        )

    # Rule 21 (ERROR): https://agentskills.io/specification#metadata-field
    # "a map from string keys to string values". yaml.safe_load hands back
    # metadata's real shape -- a dict, a list, a scalar, whatever the author
    # wrote -- instead of the hand parser's old habit of stringifying every
    # value, so the type check has to happen here rather than being true by
    # construction.
    metadata = fields.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, dict):
            findings.append(
                Finding(
                    21,
                    "ERROR",
                    rel(skill_md),
                    f"front matter 'metadata' must be a map from string keys to string values, "
                    f"got {type(metadata).__name__}",
                )
            )
        else:
            for mkey, mvalue in metadata.items():
                if not isinstance(mkey, str) or not isinstance(mvalue, str):
                    findings.append(
                        Finding(
                            21,
                            "ERROR",
                            rel(skill_md),
                            f"front matter 'metadata' entry {mkey!r}: {mvalue!r} is not a "
                            "string key with a string value",
                        )
                    )

    for entry in sorted(skill_dir.iterdir()):
        if entry.is_file() and entry.name != "SKILL.md" and entry.suffix.lower() == ".md":
            findings.append(
                Finding(11, "ERROR", rel(entry), "markdown file sits loose in the skill directory, not under references/")
            )

    declared = gather_reference_pointers(body)
    references_dir = skill_dir / "references"
    references_root = posixpath.normpath(references_dir.as_posix())
    actual_files: dict[str, Path] = {}
    if references_dir.is_dir():
        for p in sorted(references_dir.rglob("*")):
            if p.is_file():
                actual_files[f"references/{p.relative_to(references_dir).as_posix()}"] = p

    for pointer in sorted(declared):
        # Rule 22 (ERROR): a pointer declared in SKILL.md names a file the
        # skill's own references/ directory is supposed to hold -- that is
        # the whole premise the dangling-pointer and orphaned-file checks
        # below rely on. Resolve it lexically (no filesystem access, so a
        # '..' segment can't be laundered by happening to land on a file
        # that exists, such as SKILL.md itself) and require the result to
        # stay inside references/. This also catches a Markdown-link pointer
        # that never named references/ at all, e.g. "[label](b.md)".
        resolved = posixpath.normpath(posixpath.join(skill_dir.as_posix(), pointer))
        if resolved != references_root and not resolved.startswith(references_root + "/"):
            findings.append(
                Finding(
                    22,
                    "ERROR",
                    rel(skill_md),
                    f"pointer '{pointer}' does not resolve inside this skill's references/ directory",
                )
            )
            continue
        # Rule 9 (ERROR): the pointer stayed inside references/ but nothing
        # exists there.
        if not Path(resolved).is_file():
            findings.append(Finding(9, "ERROR", rel(skill_md), f"pointer '{pointer}' does not resolve to a real file"))

    # Rule 27 (ERROR): CONTRIBUTING.md's "Format" section commits to pointers
    # written as relative Markdown links, "[references/a.md](references/a.md)".
    # dfo-docs publishes each SKILL.md and its reference files as linked
    # pages, and only a link survives that as something a reader can follow.
    bare = find_bare_reference_pointers(body)
    if bare:
        findings.append(
            Finding(
                27,
                "ERROR",
                rel(skill_md),
                "bare reference pointer outside a Markdown link: "
                + ", ".join(bare)
                + f". Write each one as a Markdown link, e.g. '[{bare[0]}]({bare[0]})' (CONTRIBUTING.md 'Format').",
            )
        )

    for relpath, p in sorted(actual_files.items()):
        if relpath not in declared:
            findings.append(
                Finding(10, "ERROR", rel(p), f"{relpath} is not named by any pointer in SKILL.md and will never load")
            )

    for relpath, p in sorted(actual_files.items()):
        nested = gather_reference_pointers(p.read_text(encoding="utf-8"))
        if nested:
            findings.append(
                Finding(
                    12,
                    "ERROR",
                    rel(p),
                    f"reference file points at another references/ file, breaking the one-level-deep rule: "
                    + ", ".join(sorted(nested)),
                )
            )

    # Rule 23 (ERROR): a reference file that names another reference file by a
    # bare "<name>.md" token in prose. Rule 12 only sees "references/<name>.md"
    # tokens and "[label](target)" link targets, so a pointer written as a bare
    # filename ("See grants-loans-psi.md") used to pass silently; this closes
    # that gap. CONTRIBUTING.md's "Format" section commits to pointers staying one
    # level deep, so naming a sibling reference file at all breaks the rule:
    # carry the material inline or reach it from SKILL.md.
    for relpath, p in sorted(actual_files.items()):
        ref_text = p.read_text(encoding="utf-8")
        bare_names = set(BARE_FILENAME_RE.findall(ref_text))
        if bare_names:
            findings.append(
                Finding(
                    23,
                    "ERROR",
                    rel(p),
                    "reference file names another reference file by bare filename: "
                    + ", ".join(sorted(bare_names))
                    + ". A reference file must not point at another reference file; carry the "
                    "material inline or reach it from SKILL.md (CONTRIBUTING.md 'Format').",
                )
            )

    # Rule 25 (ERROR): a reference file's stem becomes the last segment of a
    # knowledge-graph node ID, "skill/<skill-name>/<file-stem>", and every
    # reference file's node ID is joined comma-separated into the skill's
    # 'agentSkillReferences' field. Both uses assume the stem follows the
    # same charset as a skill name (rule 5), so it is checked against the
    # same NAME_RE.
    for relpath, p in sorted(actual_files.items()):
        stem = p.stem
        if not NAME_RE.match(stem):
            findings.append(
                Finding(
                    25,
                    "ERROR",
                    rel(p),
                    f"reference file stem '{stem}' must be lowercase letters, digits and single "
                    "hyphens, with no leading, trailing or doubled hyphen, matching the skill "
                    "name format",
                )
            )

    # Rule 26 (ERROR): dfo-pipelines publishes SKILL.md's body and every
    # references/ file to the knowledge graph, dropping line breaks and
    # joining the words on either side of one -- see find_soft_line_breaks().
    # Only a blank line between paragraphs, one line per list item, headings,
    # table rows, fenced code and front matter carry meaning; any other line
    # break is incidental wrapping.
    skill_breaks = find_soft_line_breaks(text)
    if skill_breaks:
        findings.append(Finding(26, "ERROR", rel(skill_md), _soft_line_break_message(skill_breaks)))

    for relpath, p in sorted(actual_files.items()):
        ref_text = p.read_text(encoding="utf-8")
        ref_breaks = find_soft_line_breaks(ref_text)
        if ref_breaks:
            findings.append(Finding(26, "ERROR", rel(p), _soft_line_break_message(ref_breaks)))

    for relpath, p in sorted(actual_files.items()):
        ref_lines = p.read_text(encoding="utf-8").splitlines()
        if len(ref_lines) > REFERENCE_LINE_WARN and not _has_toc(ref_lines):
            findings.append(
                Finding(13, "WARNING", rel(p), f"{len(ref_lines)} lines with no table of contents near the top")
            )

    body_lines = body.splitlines()
    if len(body_lines) > SKILL_BODY_LINE_WARN:
        findings.append(
            Finding(
                14,
                "WARNING",
                rel(skill_md),
                f"body is {len(body_lines)} lines, longer than the {SKILL_BODY_LINE_WARN}-line guideline",
            )
        )

    return findings


def validate_bundle(skill_dir: Path, repo_root: Path) -> list[Finding]:
    """Check a skill directory's layout and limits against what dfo-pipelines exports.

    Rules 35 to 40, all errors: a symlink, or a file other than SKILL.md,
    attachments.yaml and Markdown under references/ (35); a file over
    MAX_FILE_BYTES (36); a file that is not UTF-8 (37); more than
    MAX_REFERENCES reference files (38); a path under the skill directory
    longer than MAX_PATH_CHARACTERS (39); a directory under references/ whose
    name is outside the skill name format (40).

    Only the files dfo-pipelines reads are decoded, so a stray binary does not
    raise rule 37 beside rule 35.
    """
    findings: list[Finding] = []
    reference_count = 0
    for path in sorted(skill_dir.rglob("*")):
        bundle_path = path.relative_to(skill_dir).as_posix()
        shown = path.relative_to(repo_root).as_posix()
        if path.is_symlink():
            findings.append(Finding(35, "ERROR", shown, "symlinks are not allowed in a skill directory"))
            continue
        if not path.is_file():
            continue
        if len(bundle_path) > MAX_PATH_CHARACTERS:
            findings.append(
                Finding(
                    39,
                    "ERROR",
                    shown,
                    f"path is {len(bundle_path)} characters, over the {MAX_PATH_CHARACTERS}-character limit",
                )
            )
        if bundle_path.startswith(f"{REFERENCES_DIRNAME}/") and bundle_path.endswith(".md"):
            reference_count += 1
            directories = bundle_path.split("/")[1:-1]
            for directory in directories:
                if not NAME_RE.fullmatch(directory):
                    findings.append(
                        Finding(
                            40,
                            "ERROR",
                            shown,
                            f"directory '{directory}' must be lowercase letters, digits and single "
                            "hyphens, with no leading, trailing or doubled hyphen, matching the skill "
                            "name format",
                        )
                    )
        elif bundle_path not in ("SKILL.md", ATTACHMENTS_FILENAME):
            # Rule 11 already names a loose Markdown file, with a clearer message.
            if not (len(path.relative_to(skill_dir).parts) == 1 and path.suffix.lower() == ".md"):
                findings.append(
                    Finding(
                        35,
                        "ERROR",
                        shown,
                        f"a skill directory holds only SKILL.md, {ATTACHMENTS_FILENAME} and Markdown "
                        f"files (.md) under {REFERENCES_DIRNAME}/",
                    )
                )
            continue
        data = path.read_bytes()
        if len(data) > MAX_FILE_BYTES:
            findings.append(
                Finding(36, "ERROR", shown, f"{len(data)} bytes is over the {MAX_FILE_BYTES}-byte limit")
            )
        try:
            data.decode("utf-8")
        except UnicodeDecodeError as exc:
            findings.append(Finding(37, "ERROR", shown, f"is not valid UTF-8: {exc}"))
    if reference_count > MAX_REFERENCES:
        findings.append(
            Finding(
                38,
                "ERROR",
                f"{skill_dir.relative_to(repo_root).as_posix()}/{REFERENCES_DIRNAME}",
                f"{reference_count} reference files is over the limit of {MAX_REFERENCES}",
            )
        )
    return findings


def _symlink_on_the_way(root: Path, repo_root: Path) -> Path | None:
    """Return the first symlink among ``root`` and its parents below ``repo_root``, if any."""
    path = repo_root
    for part in root.relative_to(repo_root).parts:
        path /= part
        if path.is_symlink():
            return path
    return None


def validate_repo(
    skills_root: Path, ontology_nodes: set[str] | None = None
) -> tuple[list[Finding], int]:
    """Validate the skills under ``skills_root`` and under ``internal/skills/`` beside it.

    Returns (findings, skill_count), counting the skills of both roots.

    Rules 50 to 53, all errors: a directory under either root has a name
    that starts with '_' (50), and it is neither validated nor counted as a
    skill; a skill name appears under both roots (51); a file sits under a
    root, where only skill directories are allowed, apart from
    categories.yaml under skills/ (52); internal/ holds anything other than
    the skills/ directory (53). A symlink under a root raises rule 35, and
    it is neither validated nor counted as a skill. Rules 55 and 56 check
    the copies of each shared rule (validate_shared_rules).

    skills/, internal/ and internal/skills/ are real directories: each one
    that is a symlink raises rule 35, because dfo-pipelines refuses to
    publish a repository it would have to read through a link. Nothing
    behind the link is read, so its skills are not counted, and the
    categories.yaml and rule 53 checks that would read through it are
    skipped. ``skills_root`` is the path as given, with a symlink in its
    last component left unresolved.
    """
    repo_root = skills_root.parent
    roots = {"installable": skills_root, "internal": repo_root / INTERNAL_SKILLS_PATH}
    findings: list[Finding] = []
    skill_names: dict[str, list[str]] = {}
    for kind, root in roots.items():
        skill_names[kind] = []
        where = root.relative_to(repo_root).as_posix()
        link = _symlink_on_the_way(root, repo_root)
        if link is not None:
            findings.append(
                Finding(
                    35,
                    "ERROR",
                    link.relative_to(repo_root).as_posix(),
                    f"is a symlink. {where}/ must be reached through real directories: "
                    "dfo-pipelines refuses to publish a repository that reads its skills through a link",
                )
            )
            continue
        for entry in sorted(root.iterdir()) if root.is_dir() else []:
            shown = entry.relative_to(repo_root).as_posix()
            if entry.is_symlink():
                findings.append(Finding(35, "ERROR", shown, "symlinks are not allowed under a skill root"))
                continue
            if not entry.is_dir():
                if kind == "installable" and entry.name == CATEGORIES_FILENAME:
                    continue
                holds = "one directory per skill"
                if kind == "installable":
                    holds += f", and {CATEGORIES_FILENAME}"
                findings.append(Finding(52, "ERROR", shown, f"{where}/ holds {holds}. This is a file"))
                continue
            if entry.name.startswith("_"):
                findings.append(
                    Finding(
                        50,
                        "ERROR",
                        shown,
                        f"directory name starts with '_', and {UNDERSCORE_CONSEQUENCE[kind]}. "
                        f"Rename it, or move it out of {where}/ if it is not a skill",
                    )
                )
                continue
            skill_names[kind].append(entry.name)
            bundle_findings = validate_bundle(entry, repo_root)
            findings.extend(bundle_findings)
            # The content checks read every file as text, so they wait for the
            # files to decode.
            if not any(f.rule == 37 for f in bundle_findings):
                findings.extend(validate_skill(entry, repo_root))
                findings.extend(validate_attachments(entry, repo_root, ontology_nodes))

    internal_dir = repo_root / INTERNAL_SKILLS_PATH.parent
    internal_is_real = internal_dir.is_dir() and not internal_dir.is_symlink()
    for entry in sorted(internal_dir.iterdir()) if internal_is_real else []:
        # A symlinked internal/skills is reported above, under rule 35.
        if entry == roots["internal"] and entry.is_symlink():
            continue
        if entry.name != INTERNAL_SKILLS_PATH.name or not entry.is_dir():
            findings.append(
                Finding(
                    53,
                    "ERROR",
                    entry.relative_to(repo_root).as_posix(),
                    f"{internal_dir.name}/ holds only the {INTERNAL_SKILLS_PATH.name}/ directory. "
                    f"A skill goes under {INTERNAL_SKILLS_PATH.as_posix()}/<name>/",
                )
            )

    for name in sorted(set(skill_names["installable"]) & set(skill_names["internal"])):
        findings.append(
            Finding(
                51,
                "ERROR",
                (roots["internal"] / name).relative_to(repo_root).as_posix(),
                f"skill '{name}' is also under {skills_root.name}/. A skill's name is its id in the graph, "
                "the Skills API and the docs site, so it sits under one root",
            )
        )
    if not skills_root.is_symlink():
        findings.extend(validate_categories(skills_root, skill_names["installable"]))
    findings.extend(validate_shared_rules(skills_root))
    return findings, sum(len(names) for names in skill_names.values())


def format_report(findings: list[Finding], skill_count: int) -> str:
    errors = sorted((f for f in findings if f.level == "ERROR"), key=lambda f: (f.rule, f.path, f.message))
    warnings = sorted((f for f in findings if f.level == "WARNING"), key=lambda f: (f.rule, f.path, f.message))

    lines: list[str] = []
    if errors:
        lines.append("Errors:")
        lines.extend(f"  {f.render()}" for f in errors)
    if warnings:
        if lines:
            lines.append("")
        lines.append("Warnings:")
        lines.extend(f"  {f.render()}" for f in warnings)
    if lines:
        lines.append("")

    summary = (
        f"{_plural(skill_count, 'skill')} checked, "
        f"{_plural(len(errors), 'error')}, "
        f"{_plural(len(warnings), 'warning')}"
    )
    lines.append(summary)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default_skills_dir = Path(__file__).resolve().parent.parent / "skills"
    parser.add_argument(
        "skills_dir",
        nargs="?",
        type=Path,
        default=default_skills_dir,
        help="path to a skills/ directory (default: this repo's own skills/); "
        f"{INTERNAL_SKILLS_PATH.as_posix()}/ beside it is validated too",
    )
    parser.add_argument(
        "--ontology-mcf",
        type=Path,
        help="compiled ontology MCF (dfo-ontology compile); also check that every "
        "'applies_to' entry is a node in it",
    )
    args = parser.parse_args(argv)

    # A symlinked skills/ keeps its own name and parent, so validate_repo sees
    # the link and reports it against the repository that holds it.
    skills_dir = args.skills_dir
    if skills_dir.is_symlink():
        skills_root = skills_dir.parent.resolve() / skills_dir.name
    else:
        skills_root = skills_dir.resolve()
    if not skills_root.is_dir():
        print(f"ERROR: {skills_root} is not a directory", file=sys.stderr)
        return 1

    ontology_nodes = None
    if args.ontology_mcf is not None:
        try:
            ontology_nodes = load_ontology_nodes(args.ontology_mcf)
        except OntologyError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

    findings, skill_count = validate_repo(skills_root, ontology_nodes)
    print(format_report(findings, skill_count))
    return 1 if any(f.level == "ERROR" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
