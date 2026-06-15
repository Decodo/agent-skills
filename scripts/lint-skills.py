#!/usr/bin/env python3
"""Validate Anthropic-format SKILL.md frontmatter for every skill in skills/.

Checks, per skill directory:
  - a SKILL.md exists
  - frontmatter has required `name` and `description`
  - `name` matches the directory name, is kebab-case, and is <= 64 chars
  - `description` is non-empty and <= 1024 chars

Exits non-zero and prints every problem found. No third-party dependencies.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NAME_MAX = 64
DESCRIPTION_MAX = 1024

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"


def parse_frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    block = parts[1]

    fields: dict[str, str] = {}
    key: str | None = None
    folded = False
    buffer: list[str] = []

    def flush() -> None:
        nonlocal key, buffer
        if key is not None:
            fields[key] = " ".join(s.strip() for s in buffer).strip()
        key, buffer = None, []

    for line in block.splitlines():
        if folded and (line.startswith(" ") or line.startswith("\t") or not line.strip()):
            buffer.append(line)
            continue
        folded = False
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            continue
        flush()
        key, value = match.group(1), match.group(2).strip()
        if value in (">-", ">", "|", "|-"):
            folded = True
            buffer = []
        else:
            buffer = [value]
    flush()
    return fields


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [f"{skill_dir.name}: missing SKILL.md"]

    fm = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    if fm is None:
        return [f"{skill_dir.name}: missing or malformed YAML frontmatter"]

    name = fm.get("name", "")
    description = fm.get("description", "")

    if not name:
        errors.append(f"{skill_dir.name}: frontmatter missing `name`")
    else:
        if name != skill_dir.name:
            errors.append(
                f"{skill_dir.name}: `name` ({name!r}) must match directory name"
            )
        if len(name) > NAME_MAX:
            errors.append(f"{skill_dir.name}: `name` exceeds {NAME_MAX} chars")
        if not NAME_RE.match(name):
            errors.append(f"{skill_dir.name}: `name` must be kebab-case [a-z0-9-]")

    if not description:
        errors.append(f"{skill_dir.name}: frontmatter missing `description`")
    elif len(description) > DESCRIPTION_MAX:
        errors.append(
            f"{skill_dir.name}: `description` is {len(description)} chars "
            f"(max {DESCRIPTION_MAX})"
        )

    return errors


def main() -> int:
    if not SKILLS_DIR.is_dir():
        print("no skills/ directory found", file=sys.stderr)
        return 1

    skill_dirs = sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir())
    if not skill_dirs:
        print("no skills found under skills/", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    for skill_dir in skill_dirs:
        all_errors.extend(validate_skill(skill_dir))

    if all_errors:
        print("SKILL.md validation failed:\n", file=sys.stderr)
        for error in all_errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"OK: {len(skill_dirs)} skill(s) validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
