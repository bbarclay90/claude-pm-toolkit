"""
Leak check: fail if tracked files contain absolute paths or personal terms.

Personal terms come from the local pdm.config.yaml (user block and
leak_check.deny), --deny arguments, and --deny-file. No terms are built in,
since a built-in list would itself leak them. Run before every push.

Usage:
  python scripts/check_clean.py
  python scripts/check_clean.py --deny Initech --deny-file ../deny.txt
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

import config

ABSOLUTE_PATH = re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/]|/(Users|home)/[^/\s]+")


def find_issues(files: dict[str, str], deny: list[str]) -> list[str]:
    patterns = [(t, re.compile(rf"(?<!\w){re.escape(t)}(?!\w)", re.IGNORECASE)) for t in deny if t]
    issues = []
    for path, text in files.items():
        for n, line in enumerate(text.splitlines(), start=1):
            if ABSOLUTE_PATH.search(line):
                issues.append(f"{path}:{n}: absolute path")
            for term, pattern in patterns:
                if pattern.search(line):
                    issues.append(f"{path}:{n}: personal term '{term}'")
    return issues


def config_terms() -> list[str]:
    try:
        user = config.user()
        extra = (config.load().get("leak_check") or {}).get("deny") or []
    except config.ConfigError:
        return []
    terms = [user["name"], *user["name"].split(), *user["aliases"], *map(str, extra)]
    return list(dict.fromkeys(terms))


def read_deny_file(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip()]


def tracked_files() -> dict[str, str]:
    root = config.repo_root()
    names = subprocess.run(
        ["git", "ls-files"], cwd=root, capture_output=True, text=True, check=True
    ).stdout.splitlines()
    files = {}
    for name in names:
        try:
            files[name] = (root / name).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
    return files


def main():
    parser = argparse.ArgumentParser(description="Check tracked files for leaks")
    parser.add_argument("--deny", action="append", default=[], help="Extra term to block")
    parser.add_argument("--deny-file", type=Path, help="File with one term to block per line")
    args = parser.parse_args()

    deny = config_terms() + args.deny
    if args.deny_file:
        deny += read_deny_file(args.deny_file)
    issues = find_issues(tracked_files(), deny)
    for issue in issues:
        print(issue)
    if issues:
        print(f"\n{len(issues)} issue(s) found.", file=sys.stderr)
        sys.exit(1)
    print("Clean: no absolute paths or personal terms in tracked files.")


if __name__ == "__main__":
    main()
