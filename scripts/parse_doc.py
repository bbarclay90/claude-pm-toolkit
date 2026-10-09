"""Extract plain text from a Word document (.docx), preserving structure."""
import sys
from pathlib import Path
import docx


def extract_text(path: str) -> str:
    doc = docx.Document(path)
    lines = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        style = para.style.name.lower()
        if style.startswith("heading 1"):
            lines.append(f"# {text}")
        elif style.startswith("heading 2"):
            lines.append(f"## {text}")
        elif style.startswith("heading 3"):
            lines.append(f"### {text}")
        else:
            lines.append(text)
    return "\n\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_doc.py <path_to_docx>", file=sys.stderr)
        sys.exit(1)
    print(extract_text(sys.argv[1]))
