import json

import setup

CONTEXT_FILES = {"overview.md", "stakeholders.md", "goals.md",
                 "roadmap-status.md", "constraints.md", "glossary.md"}


def test_add_product_creates_tree(tmp_path):
    created = setup.add_product(tmp_path, "Acme Cloud")
    product = tmp_path / "Acme Cloud"
    assert {p.name for p in (product / "_context").iterdir()} == CONTEXT_FILES
    kg = product / "Knowledge Graph"
    assert json.loads((kg / "graph.json").read_text(encoding="utf-8")) == {"nodes": [], "edges": []}
    for name in ["_index.md", "_log.md"]:
        assert (kg / name).is_file()
    for name in ["nodes", "pending", "approved"]:
        assert (kg / name).is_dir()
    assert (tmp_path / "Tasks" / "To-Do.md").is_file()
    assert product / "_context" / "overview.md" in created


def test_add_product_never_overwrites(tmp_path):
    setup.add_product(tmp_path, "Acme")
    overview = tmp_path / "Acme" / "_context" / "overview.md"
    overview.write_text("my real notes", encoding="utf-8")
    todo = tmp_path / "Tasks" / "To-Do.md"
    todo.write_text("- [ ] keep me", encoding="utf-8")

    created = setup.add_product(tmp_path, "Acme")

    assert overview.read_text(encoding="utf-8") == "my real notes"
    assert todo.read_text(encoding="utf-8") == "- [ ] keep me"
    assert created == []


import yaml

import config


def test_write_config_round_trips_windows_style_path(tmp_path):
    cfg = tmp_path / "pdm.config.yaml"
    drive = "C" + ":"
    raw = drive + "\\Users\\jane\\Obsidian Vaults\\PM"
    assert setup.write_config(cfg, "Jane Doe", ["Jane", "JD"], raw, "Acme Cloud")
    data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    assert data["vault"]["path"] == raw
    assert data["user"] == {"name": "Jane Doe", "role": "Product Manager", "aliases": ["Jane", "JD"]}
    assert data["active_product"] == "Acme Cloud"


def test_write_config_refuses_existing_without_force(tmp_path):
    cfg = tmp_path / "pdm.config.yaml"
    cfg.write_text("keep: me\n", encoding="utf-8")
    assert setup.write_config(cfg, "Jane", [], "./vault", "Acme") is False
    assert cfg.read_text(encoding="utf-8") == "keep: me\n"
    assert setup.write_config(cfg, "Jane", [], "./vault", "Acme", force=True) is True
    assert "Jane" in cfg.read_text(encoding="utf-8")


def test_local_settings_merges_existing(tmp_path):
    repo = tmp_path / "repo"
    vault = tmp_path / "vault"
    settings = repo / ".claude" / "settings.local.json"
    settings.parent.mkdir(parents=True)
    settings.write_text(json.dumps({"model": "x", "permissions": {"allow": ["Bash(ls *)"]}}), encoding="utf-8")

    assert setup.update_local_settings(settings, vault, repo) is True
    data = json.loads(settings.read_text(encoding="utf-8"))
    assert data["model"] == "x"
    assert data["permissions"]["allow"] == ["Bash(ls *)"]
    assert data["permissions"]["additionalDirectories"] == [str(vault)]

    assert setup.update_local_settings(settings, vault, repo) is False
    data = json.loads(settings.read_text(encoding="utf-8"))
    assert data["permissions"]["additionalDirectories"] == [str(vault)]


def test_local_settings_skips_vault_inside_repo(tmp_path):
    settings = tmp_path / ".claude" / "settings.local.json"
    assert setup.update_local_settings(settings, tmp_path / "vault", tmp_path) is False
    assert not settings.exists()


def test_init_end_to_end_with_spaces(tmp_path, monkeypatch):
    repo = tmp_path / "My Repo"
    repo.mkdir()
    (repo / "context").mkdir()
    (repo / "context" / "about-me.example.md").write_text("# About Me\n", encoding="utf-8")
    monkeypatch.setattr(config, "repo_root", lambda: repo)
    monkeypatch.setenv("PDM_CONFIG", str(repo / "pdm.config.yaml"))

    setup.main(["init", "--name", "Jane Doe", "--aliases", "Jane", "--vault", "./vault", "--product", "Acme Cloud"])

    assert config.product_path() == (repo / "vault" / "Acme Cloud").resolve()
    assert (repo / "context" / "about-me.md").is_file()
    assert not (repo / ".claude" / "settings.local.json").exists()


def test_jira_export_defaults_project_from_config(make_config):
    import export_jira_csv
    make_config({"user": {"name": "Jane"}, "vault": {"path": "."}, "active_product": "A",
                 "tracker": {"type": "jira", "projects": ["ABC", "DEF"]}})
    assert export_jira_csv._default_project() == "ABC"


def test_jira_export_default_project_without_tracker(make_config):
    import export_jira_csv
    make_config({"user": {"name": "Jane"}, "vault": {"path": "."}, "active_product": "A"})
    assert export_jira_csv._default_project() == ""


def test_init_refuses_existing_config_before_prompting(tmp_path, monkeypatch):
    import builtins
    import pytest
    cfg = tmp_path / "pdm.config.yaml"
    cfg.write_text("keep: me\n", encoding="utf-8")
    monkeypatch.setenv("PDM_CONFIG", str(cfg))

    def no_prompt(*args):
        raise AssertionError("init prompted before checking for an existing config")

    monkeypatch.setattr(builtins, "input", no_prompt)
    with pytest.raises(SystemExit, match="already exists"):
        setup.main(["init", "--name", "X"])
    assert cfg.read_text(encoding="utf-8") == "keep: me\n"


def test_write_config_keeps_long_vault_path_on_one_line(tmp_path):
    cfg = tmp_path / "pdm.config.yaml"
    raw = str(tmp_path / ("x" * 60) / "Ext Vault" / ("y" * 30))
    setup.write_config(cfg, "Jane", [], raw, "Acme")
    lines = cfg.read_text(encoding="utf-8").splitlines()
    path_line = next(line for line in lines if line.strip().startswith("path:"))
    assert raw in path_line


def test_init_requires_product_before_writing(tmp_path, monkeypatch):
    import builtins
    import pytest
    cfg = tmp_path / "pdm.config.yaml"
    monkeypatch.setenv("PDM_CONFIG", str(cfg))
    monkeypatch.setattr(builtins, "input", lambda *a: "")
    with pytest.raises(SystemExit, match="Product name is required"):
        setup.main(["init", "--name", "Jane", "--aliases", "Jane", "--vault", str(tmp_path / "v")])
    assert not cfg.exists()
    assert not (tmp_path / "v").exists()


STORY = "Story one\n**Summary**: Do the thing\n"


def test_jira_export_frontmatter_project_beats_config_default():
    import export_jira_csv
    text = "---\nproject: XYZ\n---\n" + STORY
    stories = export_jira_csv._parse_stories(text, "", default="ABC")
    assert stories[0]["Project"] == "XYZ"


def test_jira_export_uses_config_default_without_frontmatter():
    import export_jira_csv
    assert export_jira_csv._parse_stories(STORY, "", default="ABC")[0]["Project"] == "ABC"


def test_jira_export_argument_beats_frontmatter():
    import export_jira_csv
    text = "---\nproject: XYZ\n---\n" + STORY
    assert export_jira_csv._parse_stories(text, "ARG", default="ABC")[0]["Project"] == "ARG"
