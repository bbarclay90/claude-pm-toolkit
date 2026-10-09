from pathlib import Path

import pytest

import config


def base(vault: str, product: str = "Acme") -> dict:
    return {
        "user": {"name": "Jane Doe", "role": "Product Manager", "aliases": ["Jane"]},
        "vault": {"path": vault},
        "active_product": product,
    }


def test_missing_config_raises_with_setup_hint(tmp_path, monkeypatch):
    monkeypatch.setenv("PDM_CONFIG", str(tmp_path / "pdm.config.yaml"))
    with pytest.raises(config.ConfigError, match="setup.py init"):
        config.load()


def test_empty_config_raises(make_config):
    make_config("")
    with pytest.raises(config.ConfigError, match="setup.py init"):
        config.load()


def test_invalid_yaml_raises(make_config):
    make_config("user: [unclosed")
    with pytest.raises(config.ConfigError, match="Could not parse"):
        config.load()


def test_relative_vault_resolves_against_config_folder(make_config, tmp_path):
    (tmp_path / "vault").mkdir()
    make_config(base("./vault"))
    assert config.vault_path() == (tmp_path / "vault").resolve()


def test_absolute_vault_with_spaces(make_config, tmp_path):
    vault = tmp_path / "My Vaults" / "PM Brain"
    vault.mkdir(parents=True)
    make_config(base(str(vault)))
    assert config.vault_path() == vault


def test_tilde_vault_expands(make_config, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    (tmp_path / "notes").mkdir()
    make_config(base("~/notes"))
    assert config.vault_path() == tmp_path / "notes"


def test_missing_vault_names_resolved_path(make_config, tmp_path):
    make_config(base("./nope"))
    with pytest.raises(config.ConfigError, match="nope"):
        config.vault_path()


def test_unset_vault_path_raises(make_config):
    make_config({"user": {"name": "Jane"}, "active_product": "Acme"})
    with pytest.raises(config.ConfigError, match="vault.path"):
        config.vault_path()


def test_active_product(make_config):
    make_config(base("./vault", product="Acme Cloud"))
    assert config.active_product() == "Acme Cloud"


def test_active_product_missing_raises(make_config):
    make_config({"user": {"name": "Jane"}, "vault": {"path": "."}})
    with pytest.raises(config.ConfigError, match="active_product"):
        config.active_product()


def test_product_path_with_spaces(make_config, tmp_path):
    (tmp_path / "vault" / "Acme Cloud").mkdir(parents=True)
    make_config(base("./vault", product="Acme Cloud"))
    assert config.product_path() == (tmp_path / "vault" / "Acme Cloud").resolve()


def test_product_path_override(make_config, tmp_path):
    (tmp_path / "vault" / "Other").mkdir(parents=True)
    make_config(base("./vault"))
    assert config.product_path("Other").name == "Other"


def test_missing_product_folder_suggests_add_product(make_config, tmp_path):
    (tmp_path / "vault").mkdir()
    make_config(base("./vault"))
    with pytest.raises(config.ConfigError, match="add-product Acme"):
        config.product_path()


def test_user_defaults_aliases(make_config):
    make_config({"user": {"name": "Jane Doe"}, "vault": {"path": "."}, "active_product": "A"})
    assert config.user() == {"name": "Jane Doe", "role": "", "aliases": []}


def test_user_requires_name(make_config):
    make_config({"user": {}, "vault": {"path": "."}, "active_product": "A"})
    with pytest.raises(config.ConfigError, match="user.name"):
        config.user()
