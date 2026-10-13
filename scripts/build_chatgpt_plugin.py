#!/usr/bin/env python3
"""Build the Agent Plugins ZIP that is uploaded to ChatGPT's plugin directory.

The archive holds ``plugin.json``, ``mcp.json``, ``assets/`` and every skill
under ``skills/``, with the files at the archive root. Each skill's
``attachments.yaml`` stays out because it names graph nodes the directory has
no use for, and so do ``internal/``, ``template/`` and the rest of the
repository. The archive is deterministic: entries are sorted and carry a fixed
timestamp and creator system, so building twice from the same tree on the same
machine gives identical bytes. A different zlib build can compress the same
entries to different bytes.

Before it writes anything, the script checks the manifest against the limits
OpenAI applies to a public listing, and checks that the ChatGPT package and the
Claude plugin agree on version and server URL. Any problem is printed and the
script exits non-zero without writing.

Sources:
- Agent Plugins manifest: https://agent-plugins.org/schemas/1.0.0/plugin.schema.json
- Listing limits and review cases:
  https://developers.openai.com/apps-sdk/deploy/submission
- ZIP layout: https://developers.openai.com/plugins/deploy/submission-errors
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = REPO_ROOT / "dist" / "dfo-chatgpt-plugin.zip"

# The earliest timestamp a ZIP entry can carry. Every entry gets it, so the
# archive does not change when the files are touched.
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
# Skill files that are not part of the plugin, wherever they sit in a skill.
EXCLUDED_SKILL_FILES = {"attachments.yaml"}

# Listing limits, from the field reference on OpenAI's submission page.
DISPLAY_NAME_MAX = 30
SHORT_DESCRIPTION_MAX = 30
LONG_DESCRIPTION_MAX = 4000
DEVELOPER_NAME_MAX = 80
STARTER_PROMPTS_MAX = 3
STARTER_PROMPT_MAX = 128
CAPABILITIES_MAX = 20
CAPABILITY_MAX = 120
POSITIVE_CASES = 5
NEGATIVE_CASES = 3
CASE_FIELDS = {
    "positive": ("prompt", "tools_triggered", "expected_behavior"),
    "negative": ("prompt",),
}
URL_FIELDS = ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL")


def load_json(path: Path, problems: list[str]) -> dict:
    """Read a JSON object, recording a problem and returning {} if it fails."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        problems.append(f"{path.name}: cannot read as JSON ({exc})")
        return {}
    if not isinstance(data, dict):
        problems.append(f"{path.name}: top level is not an object")
        return {}
    return data


def check_text(
    interface: dict,
    key: str,
    limit: int,
    problems: list[str],
    *,
    one_line: bool = False,
) -> None:
    value = interface.get(key)
    if not isinstance(value, str) or not value.strip():
        problems.append(f"interface.{key}: missing or empty")
    elif len(value) > limit:
        problems.append(f"interface.{key}: {len(value)} characters, limit {limit}")
    elif one_line and "\n" in value:
        problems.append(f"interface.{key}: must be one line")


def check_string_list(
    interface: dict, key: str, count_max: int, item_max: int, problems: list[str]
) -> list[str]:
    values = interface.get(key, [])
    if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
        problems.append(f"interface.{key}: must be a list of strings")
        return []
    if len(values) > count_max:
        problems.append(f"interface.{key}: {len(values)} entries, limit {count_max}")
    for value in values:
        if len(value) > item_max:
            problems.append(
                f"interface.{key}: {len(value)} characters in {value[:30]!r}..., "
                f"limit {item_max}"
            )
    return values


def check_listing(openai: dict, problems: list[str]) -> None:
    """Check the com.openai extension against OpenAI's public listing limits."""
    interface = openai.get("interface", {})
    check_text(interface, "displayName", DISPLAY_NAME_MAX, problems)
    check_text(
        interface, "shortDescription", SHORT_DESCRIPTION_MAX, problems, one_line=True
    )
    check_text(interface, "longDescription", LONG_DESCRIPTION_MAX, problems)
    check_text(interface, "developerName", DEVELOPER_NAME_MAX, problems)
    if not isinstance(interface.get("category"), str) or not interface["category"]:
        problems.append("interface.category: missing or empty")
    for key in URL_FIELDS:
        value = interface.get(key)
        if not isinstance(value, str) or not value.startswith("https://"):
            problems.append(f"interface.{key}: must be an https URL")
    prompts = check_string_list(
        interface, "defaultPrompt", STARTER_PROMPTS_MAX, STARTER_PROMPT_MAX, problems
    )
    for prompt in prompts:
        if "@" in prompt:
            problems.append(f"interface.defaultPrompt: {prompt[:30]!r}... contains '@'")
    check_string_list(
        interface, "capabilities", CAPABILITIES_MAX, CAPABILITY_MAX, problems
    )

    cases = openai.get("review", {}).get("test_cases", {})
    for kind, expected in (("positive", POSITIVE_CASES), ("negative", NEGATIVE_CASES)):
        found = cases.get(kind, [])
        if len(found) != expected:
            problems.append(
                f"review.test_cases.{kind}: {len(found)} cases, need {expected}"
            )
        for number, case in enumerate(found, start=1):
            for field in CASE_FIELDS[kind]:
                value = case.get(field) if isinstance(case, dict) else None
                if not isinstance(value, str) or not value.strip():
                    problems.append(
                        f"review.test_cases.{kind}[{number}].{field}: missing or empty"
                    )


def check_agreement(root: Path, manifest: dict, problems: list[str]) -> None:
    """Check the ChatGPT package and the Claude plugin share a version and server."""
    claude = load_json(root / ".claude-plugin" / "plugin.json", problems)
    versions = {
        "plugin.json": manifest.get("version"),
        ".claude-plugin/plugin.json": claude.get("version"),
    }
    if len(set(versions.values())) != 1 or None in versions.values():
        problems.append(f"version differs or is missing: {versions}")

    urls: dict[str, list[str]] = {}
    for name in ("mcp.json", ".mcp.json"):
        servers = load_json(root / name, problems).get("mcpServers", {})
        urls[name] = sorted(server.get("url", "") for server in servers.values())
        if len(urls[name]) != 1:
            problems.append(
                f"{name}: must declare exactly one server, found {len(urls[name])}"
            )
    if urls["mcp.json"] != urls[".mcp.json"]:
        problems.append(f"server URL differs between mcp.json and .mcp.json: {urls}")


def check_manifest(root: Path) -> list[str]:
    problems: list[str] = []
    manifest = load_json(root / "plugin.json", problems)
    openai = manifest.get("extensions", {}).get("com.openai", {})
    check_listing(openai, problems)
    logo = openai.get("interface", {}).get("logo")
    if not isinstance(logo, str) or not (root / logo).is_file():
        problems.append(f"interface.logo: {logo!r} is not a file in the package")
    check_agreement(root, manifest, problems)
    return problems


def archive_entries(root: Path) -> list[Path]:
    """Every file that goes into the archive, sorted by archive path."""
    entries = [root / "plugin.json", root / "mcp.json"]
    entries += (p for p in (root / "assets").rglob("*") if p.is_file())
    entries += (
        p
        for p in (root / "skills").glob("*/**/*")
        if p.is_file() and p.name not in EXCLUDED_SKILL_FILES
    )
    entries = [
        p
        for p in entries
        if not any(part.startswith(".") for part in p.relative_to(root).parts)
    ]
    return sorted(entries, key=lambda p: p.relative_to(root).as_posix())


def write_archive(root: Path, output: Path) -> int:
    """Write the archive atomically and return how many entries it holds."""
    output.parent.mkdir(parents=True, exist_ok=True)
    entries = archive_entries(root)
    partial = output.with_name(output.name + ".tmp")
    try:
        with zipfile.ZipFile(partial, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in entries:
                info = zipfile.ZipInfo(path.relative_to(root).as_posix(), ZIP_TIMESTAMP)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3  # Unix, whatever machine builds the archive
                info.external_attr = 0o644 << 16
                archive.writestr(info, path.read_bytes())
        os.replace(partial, output)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    return len(entries)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="repository root to package (default: this repository)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="path of the ZIP to write (default: dist/dfo-chatgpt-plugin.zip)",
    )
    args = parser.parse_args(argv)

    problems = check_manifest(args.root)
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        return 1

    count = write_archive(args.root, args.output)
    print(f"Wrote {args.output} ({count} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
