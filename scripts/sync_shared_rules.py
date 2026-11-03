#!/usr/bin/env python3
"""Write each shared rule's text into every skill file that marks a copy of it.

A shared rule's text lives once, in ``shared-rules/<rule-id>.md``. Each skill
that states the rule holds a copy between two marker lines:

    <!-- shared:<rule-id> -->

    The rule's text.

    <!-- /shared:<rule-id> -->

The script replaces the text between every pair of markers with its source,
skipping markers inside fenced code blocks. It writes nothing if a source is
malformed, a file's markers are broken or out of their written form (indented,
inside a list item or blockquote, or without blank lines around them), or a
marker names a rule with no source, and it then exits non-zero.
scripts/validate_skills.py fails on any copy that differs from its source.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_skills import (  # noqa: E402
    SHARED_RULES_DIRNAME,
    load_shared_sources,
    parse_shared_blocks,
    skill_markdown_files,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def sync(repo_root: Path) -> tuple[dict[Path, str], list[str]]:
    """The new text of each skill file whose marked copies differ from their
    sources, and every problem that stops the sync."""
    sources, findings = load_shared_sources(repo_root)
    problems = [finding.render() for finding in findings]
    updates: dict[Path, str] = {}
    for path in skill_markdown_files(repo_root / "skills"):
        shown = path.relative_to(repo_root).as_posix()
        try:
            text = path.read_bytes().decode("utf-8")  # keeps carriage returns for the marker check
        except UnicodeDecodeError:
            problems.append(f"{shown}: is not valid UTF-8")
            continue
        blocks, marker_problems = parse_shared_blocks(text)
        problems += (f"{shown}: {problem}" for problem in marker_problems)
        if marker_problems:
            continue
        synced = text
        for block in reversed(blocks):
            if block.rule_id not in sources:
                source = f"{SHARED_RULES_DIRNAME}/{block.rule_id}.md"
                problems.append(f"{shown}: marks shared rule '{block.rule_id}', and {source} does not exist")
                continue
            synced = f"{synced[: block.start]}\n\n{sources[block.rule_id]}\n\n{synced[block.end :]}"
        if synced != text:
            updates[path] = synced
    return updates, problems


def main(repo_root: Path = REPO_ROOT) -> int:
    updates, problems = sync(repo_root)
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    for path, text in updates.items():
        path.write_bytes(text.encode("utf-8"))
        print(f"updated {path.relative_to(repo_root).as_posix()}")
    print(f"{len(updates)} file{'' if len(updates) == 1 else 's'} updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
