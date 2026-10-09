"""
Configuration loader for the PM toolkit.

Reads pdm.config.yaml from the repo root (or the path in the PDM_CONFIG
environment variable) and resolves the vault and product paths.

Usage:
  import config
  config.vault_path()      # resolved vault folder
  config.active_product()  # e.g. "Acme"
  config.product_path()    # vault / active product
"""
import os
from pathlib import Path

import yaml

CONFIG_NAME = "pdm.config.yaml"
SETUP_HINT = "Run `python scripts/setup.py init` to create it"


class ConfigError(Exception):
    pass


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def config_file() -> Path:
    override = os.environ.get("PDM_CONFIG")
    return Path(override) if override else repo_root() / CONFIG_NAME


def load() -> dict:
    path = config_file()
    if not path.exists():
        raise ConfigError(f"Config not found at {path}. {SETUP_HINT}.")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise ConfigError(f"Could not parse {path}: {e}") from e
    if not isinstance(data, dict):
        raise ConfigError(f"{path} is empty or not a mapping. {SETUP_HINT}.")
    return data


def resolve_vault(raw: str, base: Path) -> Path:
    path = Path(os.path.expanduser(raw))
    return path if path.is_absolute() else (base / path).resolve()


def vault_path() -> Path:
    raw = (load().get("vault") or {}).get("path")
    if not raw:
        raise ConfigError(f"vault.path is not set in {config_file()}.")
    path = resolve_vault(str(raw), config_file().parent)
    if not path.is_dir():
        raise ConfigError(f"Vault folder does not exist: {path}")
    return path


def active_product() -> str:
    product = load().get("active_product")
    if not product:
        raise ConfigError(f"active_product is not set in {config_file()}.")
    return str(product)


def product_path(product: str | None = None) -> Path:
    name = product or active_product()
    path = vault_path() / name
    if not path.is_dir():
        raise ConfigError(
            f"Product folder does not exist: {path}. "
            f"Run `python scripts/setup.py add-product {name}`."
        )
    return path


def user() -> dict:
    data = load().get("user") or {}
    if not data.get("name"):
        raise ConfigError(f"user.name is not set in {config_file()}.")
    return {
        "name": str(data["name"]),
        "role": str(data.get("role") or ""),
        "aliases": [str(a) for a in data.get("aliases") or []],
    }
