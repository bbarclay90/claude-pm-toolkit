"""
Set up the PM toolkit for a new user or a new product.

Usage:
  python scripts/setup.py init
  python scripts/setup.py add-product "Product Name"
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

import yaml

import config

CONTEXT_STUBS = config.repo_root() / "templates" / "vault" / "_context"

TODO_HEADER = """# To-Do

Items are added automatically by /project:new-notes. Check them off as you complete them.

---
"""

INDEX_HEADER = """# Knowledge Graph Index

This file is auto-updated by /project:approve-context. Do not edit manually.
"""


def _write_new(path: Path, text: str, created: list[Path]) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    created.append(path)


def add_product(vault: Path, name: str) -> list[Path]:
    created: list[Path] = []
    product = vault / name

    for stub in sorted(CONTEXT_STUBS.glob("*.md")):
        target = product / "_context" / stub.name
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(stub, target)
            created.append(target)

    kg = product / "Knowledge Graph"
    _write_new(kg / "graph.json", json.dumps({"nodes": [], "edges": []}, indent=2), created)
    _write_new(kg / "_index.md", INDEX_HEADER, created)
    _write_new(kg / "_log.md", "# Knowledge Graph Log\n\n", created)
    for folder in ["nodes", "pending", "approved"]:
        (kg / folder).mkdir(parents=True, exist_ok=True)

    _write_new(vault / "Tasks" / "To-Do.md", TODO_HEADER, created)
    return created


def cmd_add_product(args) -> None:
    try:
        vault = config.vault_path()
    except config.ConfigError as e:
        sys.exit(f"Error: {e}")
    created = add_product(vault, args.name)
    print(f"Product '{args.name}' ready at {vault / args.name} ({len(created)} files created).")


def write_config(path: Path, name: str, aliases: list[str], vault: str,
                 product: str, force: bool = False) -> bool:
    if path.exists() and not force:
        return False
    data = {
        "user": {"name": name, "role": "Product Manager", "aliases": aliases},
        "vault": {"path": vault},
        "active_product": product,
    }
    text = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=float("inf"))
    path.write_text(text, encoding="utf-8")
    return True


def update_local_settings(settings_file: Path, vault: Path, repo: Path) -> bool:
    if vault.resolve().is_relative_to(repo.resolve()):
        return False
    data = json.loads(settings_file.read_text(encoding="utf-8")) if settings_file.exists() else {}
    dirs = data.setdefault("permissions", {}).setdefault("additionalDirectories", [])
    if str(vault) in dirs:
        return False
    dirs.append(str(vault))
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    settings_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return True


def _ask(value: str | None, prompt: str, default: str = "") -> str:
    if value:
        return value
    suffix = f" [{default}]" if default else ""
    answer = input(f"{prompt}{suffix}: ").strip()
    return answer or default


def cmd_init(args) -> None:
    repo = config.repo_root()
    cfg = config.config_file()
    if cfg.exists() and not args.force:
        sys.exit(f"{cfg} already exists. Re-run with --force to overwrite it.")
    name = _ask(args.name, "Your name")
    aliases_raw = _ask(args.aliases, "Aliases used for you in meetings (comma separated)", name.split()[0])
    aliases = [a.strip() for a in aliases_raw.split(",") if a.strip()]
    vault_raw = _ask(args.vault, "Vault path", "./vault")
    product = _ask(args.product, "First product name")
    if not product:
        sys.exit("Product name is required. Re-run init and enter one.")

    if not write_config(cfg, name, aliases, vault_raw, product, args.force):
        sys.exit(f"{cfg} already exists. Re-run with --force to overwrite it.")
    print(f"Wrote {cfg}")

    about = repo / "context" / "about-me.md"
    if not about.exists():
        shutil.copyfile(repo / "context" / "about-me.example.md", about)
        print(f"Wrote {about}")

    vault = config.resolve_vault(vault_raw, cfg.parent)
    vault.mkdir(parents=True, exist_ok=True)
    add_product(vault, product)

    if update_local_settings(repo / ".claude" / "settings.local.json", vault, repo):
        print("Added the vault to .claude/settings.local.json so Claude Code can access it.")

    try:
        config.product_path()
    except config.ConfigError as e:
        sys.exit(f"Error: {e}")
    print(f"Setup complete. Vault: {vault} | Product: {product}")


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="PM toolkit setup")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create pdm.config.yaml and the first product")
    p_init.add_argument("--name")
    p_init.add_argument("--aliases", help="Comma separated")
    p_init.add_argument("--vault")
    p_init.add_argument("--product")
    p_init.add_argument("--force", action="store_true", help="Overwrite an existing config")
    p_init.set_defaults(func=cmd_init)

    p_add = sub.add_parser("add-product", help="Create the vault folders for a product")
    p_add.add_argument("name")
    p_add.set_defaults(func=cmd_add_product)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
