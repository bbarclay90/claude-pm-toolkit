"""
Convert a user story map markdown file to a FigJam-ready text format.

Output is a structured plain text file where each swim lane (Activity) is
labeled, tasks appear as section headers, and each story is on its own line.
Copy the output into FigJam using Paste to Sticky Notes (one sticky per line).
"""
import re
import sys
from pathlib import Path

DOCS_DIR = Path(__file__).parent.parent / "docs" / "output"


def convert(md_path: str) -> Path:
    path = Path(md_path)
    text = path.read_text(encoding="utf-8")

    # Strip YAML frontmatter
    text = re.sub(r"^---.*?---\n", "", text, flags=re.DOTALL)

    output_lines = []
    current_activity = None
    current_task = None

    for line in text.splitlines():
        if line.startswith("## ") and not line.startswith("## Release"):
            current_activity = line[3:].strip()
            output_lines.append(f"\n=== ACTIVITY: {current_activity} ===\n")
        elif line.startswith("### "):
            current_task = line[4:].strip()
            output_lines.append(f"--- {current_task} ---")
        elif line.startswith("- Story:"):
            story = line[8:].strip()
            output_lines.append(story)
        elif line.startswith("- ") and current_task:
            output_lines.append(line[2:].strip())

    out_path = DOCS_DIR / (path.stem + "_figjam.txt")
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(output_lines), encoding="utf-8")

    print(f"Saved: {out_path}")
    print("\nTo use in FigJam:")
    print("  1. Open the output file and copy all contents")
    print("  2. In FigJam: Edit > Paste as sticky notes")
    print("  Activity headers (===) and task headers (---) are separators - delete after pasting")
    return out_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python export_figjam.py <path_to_md>", file=sys.stderr)
        sys.exit(1)
    convert(sys.argv[1])
