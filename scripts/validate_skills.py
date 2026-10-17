#!/usr/bin/env python3
"""Validate every Skill in this repo against Anthropic's Agent Skills spec.

A "Skill" is any directory containing a SKILL.md file. This script finds all
of them and checks:

  - YAML frontmatter exists and parses
  - required fields `name` and `description` are present and well-formed
    (per https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
  - `name` is unique across the repo
  - files the SKILL.md body references (markdown links or inline code paths
    under scripts/, references/, assets/) actually exist
  - best-practice checks (SKILL.md body under 500 lines, long reference
    files have a table of contents, no Windows-style backslash paths) are
    reported as warnings rather than failing the build
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency: pyyaml. Install it with `pip install pyyaml`.", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
SKIP_DIR_NAMES = {".git", ".github", "node_modules"}

MAX_NAME_LEN = 64
MAX_DESC_LEN = 1024
MAX_BODY_LINES = 500
MAX_REFERENCE_LINES_WITHOUT_TOC = 100

NAME_PATTERN = re.compile(r"^[a-z0-9-]+$")
RESERVED_WORDS = ("anthropic", "claude")
XML_TAG_PATTERN = re.compile(r"</?[a-zA-Z][^>]*>")

MARKDOWN_LINK_PATTERN = re.compile(r"\]\(([^)\s]+)\)")
BACKTICK_PATTERN = re.compile(r"`([^`\n]+)`")
BUNDLED_PATH_PATTERN = re.compile(r"(?:^|[\s\"'(])((?:scripts|references|reference|assets)/[\w./-]+\.\w+)")
WINDOWS_PATH_PATTERN = re.compile(r"[\w][\\][\w./\\-]*\.\w+")


@dataclass
class Issue:
    level: str  # "error" or "warning"
    skill: str
    message: str

    def __str__(self) -> str:
        marker = "ERROR" if self.level == "error" else "WARN "
        return f"[{marker}] {self.skill}: {self.message}"


def find_skills(root: Path):
    for path in sorted(root.rglob("SKILL.md")):
        if any(part in SKIP_DIR_NAMES for part in path.relative_to(root).parts):
            continue
        yield path.parent


def parse_frontmatter(text: str):
    """Split SKILL.md into (frontmatter_dict, body). Raises ValueError on bad YAML."""
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    _, raw_frontmatter, body = parts
    try:
        data = yaml.safe_load(raw_frontmatter)
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML frontmatter ({exc})") from exc
    return (data or {}), body


def check_resource_references(skill_dir: Path, body: str, rel: str, issues: list[Issue]) -> None:
    checked: set[str] = set()

    for match in MARKDOWN_LINK_PATTERN.finditer(body):
        target = match.group(1).split("#")[0].strip()
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        checked.add(target)

    for backtick_match in BACKTICK_PATTERN.finditer(body):
        for path_match in BUNDLED_PATH_PATTERN.finditer(" " + backtick_match.group(1)):
            checked.add(path_match.group(1))

    for target in sorted(checked):
        if not (skill_dir / target).resolve().exists():
            issues.append(Issue("error", rel, f"referenced file '{target}' does not exist"))


def validate_name(name: object, rel: str, dir_name: str, issues: list[Issue]) -> None:
    if not name:
        issues.append(Issue("error", rel, "frontmatter missing required field 'name'"))
        return
    name = str(name)
    if len(name) > MAX_NAME_LEN:
        issues.append(Issue("error", rel, f"name exceeds {MAX_NAME_LEN} characters ({len(name)})"))
    if not NAME_PATTERN.match(name):
        issues.append(Issue("error", rel, f"name '{name}' must contain only lowercase letters, numbers, and hyphens"))
    if XML_TAG_PATTERN.search(name):
        issues.append(Issue("error", rel, "name must not contain XML tags"))
    lowered = name.lower()
    for word in RESERVED_WORDS:
        if word in lowered:
            issues.append(Issue("error", rel, f"name must not contain reserved word '{word}'"))
    if name != dir_name:
        issues.append(Issue("warning", rel, f"frontmatter name '{name}' does not match directory name '{dir_name}'"))


def validate_description(description: object, rel: str, issues: list[Issue]) -> None:
    if description is None or not str(description).strip():
        issues.append(Issue("error", rel, "frontmatter missing required non-empty field 'description'"))
        return
    description = str(description)
    if len(description) > MAX_DESC_LEN:
        issues.append(Issue("error", rel, f"description exceeds {MAX_DESC_LEN} characters ({len(description)})"))
    if XML_TAG_PATTERN.search(description):
        issues.append(Issue("error", rel, "description must not contain XML tags"))


def check_reference_tocs(skill_dir: Path, rel: str, issues: list[Issue]) -> None:
    for dir_name in ("references", "reference"):
        ref_dir = skill_dir / dir_name
        if not ref_dir.is_dir():
            continue
        for ref_file in sorted(ref_dir.rglob("*.md")):
            lines = ref_file.read_text(encoding="utf-8", errors="replace").splitlines()
            if len(lines) <= MAX_REFERENCE_LINES_WITHOUT_TOC:
                continue
            head = "\n".join(lines[:15]).lower()
            if "contents" not in head and "table of contents" not in head:
                issues.append(Issue(
                    "warning", rel,
                    f"{ref_file.relative_to(skill_dir)} is {len(lines)} lines with no table of contents "
                    f"in its first 15 lines",
                ))


def validate_skill(skill_dir: Path, root: Path) -> list[Issue]:
    issues: list[Issue] = []
    rel = str(skill_dir.relative_to(root)) or "."
    skill_md = skill_dir / "SKILL.md"

    try:
        text = skill_md.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return [Issue("error", rel, f"SKILL.md is not valid UTF-8 ({exc})")]

    try:
        frontmatter, body = parse_frontmatter(text)
    except ValueError as exc:
        return [Issue("error", rel, str(exc))]

    if frontmatter is None:
        return [Issue("error", rel, "missing YAML frontmatter (file must start with '---')")]
    if not isinstance(frontmatter, dict):
        return [Issue("error", rel, "frontmatter must be a YAML mapping")]

    validate_name(frontmatter.get("name"), rel, skill_dir.name, issues)
    validate_description(frontmatter.get("description"), rel, issues)

    body_lines = body.strip("\n").splitlines()
    if len(body_lines) > MAX_BODY_LINES:
        issues.append(Issue(
            "warning", rel,
            f"SKILL.md body is {len(body_lines)} lines; keep under {MAX_BODY_LINES} for optimal performance",
        ))

    if WINDOWS_PATH_PATTERN.search(body):
        issues.append(Issue("warning", rel, "possible Windows-style backslash path found; use forward slashes"))

    check_resource_references(skill_dir, body, rel, issues)
    check_reference_tocs(skill_dir, rel, issues)

    return issues


def main() -> int:
    skill_dirs = list(find_skills(REPO_ROOT))

    if not skill_dirs:
        print("No SKILL.md files found in this repo — nothing to validate.")
        return 0

    all_issues: list[Issue] = []
    names_seen: dict[str, str] = {}

    for skill_dir in skill_dirs:
        rel = str(skill_dir.relative_to(REPO_ROOT))
        issues = validate_skill(skill_dir, REPO_ROOT)
        all_issues.extend(issues)

        try:
            frontmatter, _ = parse_frontmatter((skill_dir / "SKILL.md").read_text(encoding="utf-8"))
        except (ValueError, OSError):
            frontmatter = None
        name = (frontmatter or {}).get("name") if isinstance(frontmatter, dict) else None
        if name:
            if name in names_seen:
                all_issues.append(Issue(
                    "error", rel,
                    f"duplicate skill name '{name}' also used by '{names_seen[name]}'",
                ))
            else:
                names_seen[name] = rel

    errors = [i for i in all_issues if i.level == "error"]
    warnings = [i for i in all_issues if i.level == "warning"]

    print(f"Found {len(skill_dirs)} skill(s). {len(errors)} error(s), {len(warnings)} warning(s).\n")
    for issue in sorted(all_issues, key=lambda i: (i.skill, i.level)):
        print(issue)

    print()
    if errors:
        print(f"FAILED: {len(errors)} error(s) found.")
        return 1

    print("All skills passed validation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
