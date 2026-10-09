import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))


@pytest.fixture
def make_config(tmp_path, monkeypatch):
    """Write a pdm.config.yaml in tmp_path and point PDM_CONFIG at it."""
    def _make(data) -> Path:
        cfg = tmp_path / "pdm.config.yaml"
        if isinstance(data, str):
            cfg.write_text(data, encoding="utf-8")
        else:
            cfg.write_text(yaml.safe_dump(data), encoding="utf-8")
        monkeypatch.setenv("PDM_CONFIG", str(cfg))
        return cfg
    return _make
