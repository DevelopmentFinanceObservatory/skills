"""Tests for scripts/build_chatgpt_plugin.py.

Runnable with a stock interpreter: ``python -m unittest discover``. Each test
packages a copy of this repository's own plugin files inside a TemporaryDirectory.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "build_chatgpt_plugin.py"

_spec = importlib.util.spec_from_file_location("build_chatgpt_plugin", SCRIPT_PATH)
build_chatgpt_plugin = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
sys.modules["build_chatgpt_plugin"] = build_chatgpt_plugin
_spec.loader.exec_module(build_chatgpt_plugin)

MANIFEST_PATHS = ("plugin.json", "mcp.json", ".mcp.json", ".claude-plugin", "assets")


def copy_package(destination: Path) -> Path:
    """Copy the manifests and assets the build reads from this repository."""
    destination.mkdir()
    for name in MANIFEST_PATHS:
        source = REPO_ROOT / name
        if source.is_dir():
            shutil.copytree(source, destination / name)
        else:
            shutil.copy(source, destination / name)
    return destination


def write_files(root: Path, files: list[str]) -> None:
    for name in files:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x\n")


def rewrite_json(path: Path, change) -> None:
    data = json.loads(path.read_text())
    change(data)
    path.write_text(json.dumps(data))


def build(root: Path, output: Path) -> tuple[int, str]:
    stderr = io.StringIO()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
        code = build_chatgpt_plugin.main(["--root", str(root), "--output", str(output)])
    return code, stderr.getvalue()


def interface(data: dict) -> dict:
    return data["extensions"]["com.openai"]["interface"]


def cases(data: dict) -> dict:
    return data["extensions"]["com.openai"]["review"]["test_cases"]


class BuildChatgptPluginTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.output = self.tmp / "dist" / "plugin.zip"

    def test_archive_from_this_repository_holds_the_public_skills(self) -> None:
        root = copy_package(self.tmp / "repo")
        for name in ("skills", "internal"):
            shutil.copytree(REPO_ROOT / name, root / name)

        code, stderr = build(root, self.output)

        self.assertEqual(code, 0, stderr)
        with zipfile.ZipFile(self.output) as archive:
            names = archive.namelist()
        self.assertTrue({"plugin.json", "mcp.json", "assets/logo.svg"} <= set(names))
        skills_in_archive = {n.split("/")[1] for n in names if n.startswith("skills/")}
        public_skills = {p.name for p in (REPO_ROOT / "skills").iterdir() if p.is_dir()}
        self.assertEqual(skills_in_archive, public_skills)
        self.assertFalse([n for n in names if n.endswith("attachments.yaml")])
        self.assertFalse([n for n in names if n.startswith("internal/")])

    def test_archive_leaves_out_everything_but_skill_content(self) -> None:
        root = copy_package(self.tmp / "repo")
        write_files(
            root,
            [
                "skills/a-skill/SKILL.md",
                "skills/a-skill/references/r.md",
                "skills/a-skill/attachments.yaml",
                "skills/a-skill/references/attachments.yaml",
                "skills/a-skill/.hidden",
                "skills/a-skill/.cache/x.md",
                "skills/categories.yaml",
                "skills/loose.md",
                "internal/skills/i/SKILL.md",
                "template/SKILL.md",
                "assets/.DS_Store",
            ],
        )

        code, stderr = build(root, self.output)

        self.assertEqual(code, 0, stderr)
        with zipfile.ZipFile(self.output) as archive:
            self.assertEqual(
                archive.namelist(),
                [
                    "assets/logo.svg",
                    "mcp.json",
                    "plugin.json",
                    "skills/a-skill/SKILL.md",
                    "skills/a-skill/references/r.md",
                ],
            )

    def test_entries_are_sorted_whatever_order_the_filesystem_lists(self) -> None:
        root = copy_package(self.tmp / "repo")
        write_files(root, [f"skills/{n}/SKILL.md" for n in ("b-skill", "a-skill")])

        def reversed_listing(original):
            def listing(self, *args, **kwargs):
                return iter(sorted(original(self, *args, **kwargs), reverse=True))

            return listing

        with (
            mock.patch.object(Path, "glob", reversed_listing(Path.glob)),
            mock.patch.object(Path, "rglob", reversed_listing(Path.rglob)),
        ):
            entries = build_chatgpt_plugin.archive_entries(root)

        names = [p.relative_to(root).as_posix() for p in entries]
        self.assertEqual(names, sorted(names))
        self.assertEqual(len(names), 5)

    def test_archive_is_byte_identical_across_builds(self) -> None:
        root = copy_package(self.tmp / "repo")
        write_files(root, ["skills/a-skill/SKILL.md"])
        build(root, self.output)
        first = self.output.read_bytes()
        for path in root.rglob("*"):
            path.touch()
        build(root, self.output)
        self.assertEqual(self.output.read_bytes(), first)

    def test_a_broken_manifest_fails_without_writing(self) -> None:
        def long_name(data: dict) -> None:
            interface(data)["displayName"] = "x" * 31

        def four_prompts(data: dict) -> None:
            interface(data)["defaultPrompt"] = ["a", "b", "c", "d"]

        def mention(data: dict) -> None:
            interface(data)["defaultPrompt"] = ["Ask @dfo for aid data."]

        def four_positive_cases(data: dict) -> None:
            cases(data)["positive"].pop()

        def http_url(data: dict) -> None:
            interface(data)["privacyPolicyURL"] = (
                "http://developmentfinance.org/privacy"
            )

        def no_expected_behavior(data: dict) -> None:
            del cases(data)["positive"][0]["expected_behavior"]

        for change in (
            long_name,
            four_prompts,
            mention,
            four_positive_cases,
            http_url,
            no_expected_behavior,
        ):
            with self.subTest(change=change.__name__):
                root = copy_package(self.tmp / change.__name__)
                rewrite_json(root / "plugin.json", change)
                output = self.tmp / f"{change.__name__}.zip"

                code, stderr = build(root, output)

                self.assertEqual(code, 1)
                self.assertIn("ERROR:", stderr)
                self.assertFalse(output.exists())
                self.assertFalse(output.with_name(output.name + ".tmp").exists())

    def test_manifests_that_disagree_fail(self) -> None:
        def set_version(data: dict) -> None:
            data["version"] = "9.9.9"

        def move_server(data: dict) -> None:
            data["mcpServers"]["dfo"]["url"] = "https://example.com/mcp"

        for name, path, change in (
            ("claude_version", ".claude-plugin/plugin.json", set_version),
            ("plugin_version", "plugin.json", set_version),
            ("claude_server", ".mcp.json", move_server),
            ("package_server", "mcp.json", move_server),
        ):
            with self.subTest(disagreement=name):
                root = copy_package(self.tmp / name)
                rewrite_json(root / path, change)
                output = self.tmp / f"{name}.zip"

                code, _ = build(root, output)

                self.assertEqual(code, 1)
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
