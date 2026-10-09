import check_clean

DRIVE = "C" + ":"
USERS = "/" + "Users" + "/"


def test_flags_windows_drive_path():
    issues = check_clean.find_issues({"a.md": f"see {DRIVE}\\data\\x"}, [])
    assert issues == ["a.md:1: absolute path"]


def test_flags_forward_slash_drive_path():
    assert check_clean.find_issues({"a.py": f'P = "{DRIVE}/x"'}, [])


def test_flags_users_path():
    assert check_clean.find_issues({"a.md": f"{USERS}jane/vault"}, [])


def test_ignores_urls_and_relative_paths():
    text = "https://example.com/a\n./vault\n~/notes\n{vault}/{product}/x"
    assert check_clean.find_issues({"a.md": text}, []) == []


def test_flags_deny_term_whole_word_case_sensitive():
    files = {"a.md": "line one\nAuthor: Jane Doe"}
    assert check_clean.find_issues(files, ["Jane"]) == ["a.md:2: personal term 'Jane'"]


def test_deny_term_does_not_match_inside_word():
    assert check_clean.find_issues({"a.md": "Janet and Annex"}, ["Jane", "Ann"]) == []


def test_ships_without_builtin_terms():
    assert not hasattr(check_clean, "DEFAULT_DENY")


def test_config_terms_from_local_config(make_config):
    make_config({
        "user": {"name": "Jane Doe", "aliases": ["JD"]},
        "vault": {"path": "."},
        "active_product": "A",
        "leak_check": {"deny": ["Initech"]},
    })
    assert set(check_clean.config_terms()) == {"Jane Doe", "Jane", "Doe", "JD", "Initech"}


def test_read_deny_file(tmp_path):
    f = tmp_path / "deny.txt"
    f.write_text("Initech\n\n  Globex  \n", encoding="utf-8")
    assert check_clean.read_deny_file(f) == ["Initech", "Globex"]


def test_config_terms_without_config(tmp_path, monkeypatch):
    monkeypatch.setenv("PDM_CONFIG", str(tmp_path / "missing.yaml"))
    assert check_clean.config_terms() == []


def test_deny_term_matches_lowercase_slug():
    issues = check_clean.find_issues({"a.md": "id: stakeholder-ann"}, ["Ann"])
    assert issues == ["a.md:1: personal term 'Ann'"]
