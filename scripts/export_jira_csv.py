"""Convert a user stories markdown file to a Jira-importable CSV.

Columns: Project, Issue Type, Summary, Description
- Issue Type is always Story
- Summary: pulled from the **Summary** field in each story block (7 words max)
- Description: full formatted block with value statement, user story, tasks,
  AC, NFRs, tech signoff, dependencies, and risks
"""
import csv
import re
import sys
from pathlib import Path

DOCS_DIR = Path(__file__).parent.parent / "docs" / "output"
JIRA_COLUMNS = ["Project", "Issue Type", "Summary", "Description"]


def _extract_field(block: str, label: str) -> str:
    pattern = rf"\*\*{re.escape(label)}\*\*:\s*(.+)"
    match = re.search(pattern, block)
    return match.group(1).strip() if match else ""


def _extract_section(block: str, heading: str) -> str:
    pattern = rf"{re.escape(heading)}:\n(.*?)(?=\n[A-Z][^\n]+:\n|\Z)"
    match = re.search(pattern, block, re.DOTALL)
    return match.group(1).strip() if match else ""


def _build_description(block: str) -> str:
    sections = []

    # Value statement: first non-blank paragraph after the metadata fields
    meta_end = max(
        block.rfind("**Project**:"),
        block.rfind("**Summary**:"),
    )
    after_meta = block[meta_end:].split("\n", 2)[-1] if meta_end != -1 else block
    value_lines = []
    for line in after_meta.splitlines():
        stripped = line.strip()
        if stripped.startswith("User Story:") or stripped.startswith("Tasks:"):
            break
        if stripped and not stripped.startswith("**"):
            value_lines.append(stripped)
    if value_lines:
        sections.append(" ".join(value_lines))

    # User story
    user_story = _extract_section(block, "User Story")
    if user_story:
        sections.append(f"User Story:\n{user_story}")

    # Tasks
    tasks = _extract_section(block, "Tasks")
    if tasks:
        sections.append(f"Tasks:\n{tasks}")

    # Acceptance Criteria
    ac = _extract_section(block, "Acceptance Criteria")
    if ac:
        sections.append(f"Acceptance Criteria:\n{ac}")

    # Non-Functional Requirements
    nfr = _extract_section(block, "Non-Functional Requirements")
    if nfr:
        sections.append(f"Non-Functional Requirements:\n{nfr}")

    # Technical/Architecture Signoff
    tech = _extract_section(block, "Technical/Architecture Signoff")
    if tech:
        sections.append(f"Technical/Architecture Signoff:\n{tech}")

    # Dependencies
    deps = _extract_section(block, "Dependencies")
    if deps:
        sections.append(f"Dependencies:\n{deps}")

    # Risks
    risks = _extract_section(block, "Risks")
    if risks:
        sections.append(f"Risks:\n{risks}")

    return "\n\n".join(sections)


def _parse_stories(text: str, project: str, default: str = "") -> list[dict]:
    # Strip YAML frontmatter and extract project name if not provided
    fm_match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if fm_match and not project:
        proj_match = re.search(r"^project:\s*(.+)", fm_match.group(1), re.MULTILINE)
        if proj_match:
            project = proj_match.group(1).strip()
    project = project or default
    text = re.sub(r"^---.*?---\n", "", text, flags=re.DOTALL)

    stories = []
    blocks = re.split(r"\n---\n", text)

    for block in blocks:
        block = block.strip()
        if not block or block.startswith("#"):
            continue

        lines = block.splitlines()
        title_line = lines[0].strip().lstrip("# ").strip()
        if not title_line or title_line.startswith("Stories:"):
            continue

        summary = _extract_field(block, "Summary")
        if not summary or summary.startswith("("):
            # Fall back to deriving from title
            summary = " ".join(title_line.split()[:7])

        story_project = _extract_field(block, "Project") or project

        stories.append({
            "Project": story_project,
            "Issue Type": "Story",
            "Summary": summary,
            "Description": _build_description(block),
        })

    return stories


def convert(md_path: str, project: str = "", default: str = "") -> Path:
    path = Path(md_path)
    text = path.read_text(encoding="utf-8")
    stories = _parse_stories(text, project, default)

    out_path = DOCS_DIR / (path.stem + ".csv")
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=JIRA_COLUMNS)
        writer.writeheader()
        writer.writerows(stories)

    print(f"Saved {len(stories)} stories to: {out_path}")
    return out_path


def _default_project() -> str:
    try:
        import config
        projects = (config.load().get("tracker") or {}).get("projects") or []
        return str(projects[0]) if projects else ""
    except Exception:
        return ""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python export_jira_csv.py <path_to_md> [project_key]", file=sys.stderr)
        sys.exit(1)
    project_arg = sys.argv[2] if len(sys.argv) > 2 else ""
    convert(sys.argv[1], project_arg, default=_default_project())
