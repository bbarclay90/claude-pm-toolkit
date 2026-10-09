import pytest

import config
import knowledge_graph as kg


def cfg(product="Acme"):
    return {"user": {"name": "Jane"}, "vault": {"path": "./vault"}, "active_product": product}


def test_active_product_from_config(make_config):
    make_config(cfg("Acme Cloud"))
    assert kg.get_active_product() == "Acme Cloud"


def test_active_product_override(make_config):
    make_config(cfg())
    assert kg.get_active_product("Other") == "Other"


def test_kg_dir_under_vault_product(make_config, tmp_path):
    (tmp_path / "vault" / "Acme Cloud").mkdir(parents=True)
    make_config(cfg("Acme Cloud"))
    assert kg.get_kg_dir("Acme Cloud") == (tmp_path / "vault" / "Acme Cloud" / "Knowledge Graph").resolve()


def test_kg_dir_missing_product_raises(make_config, tmp_path):
    (tmp_path / "vault").mkdir()
    make_config(cfg())
    with pytest.raises(config.ConfigError, match="add-product"):
        kg.get_kg_dir("Acme")


def test_no_hardcoded_vault():
    assert not hasattr(kg, "VAULT")
    assert not hasattr(kg, "ACTIVE_PRODUCT_FILE")
