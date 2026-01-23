import sys

from src.nastrajacz import main


def test_apply_copies_single_file_to_system(tmp_path, monkeypatch, capsys):
    """--apply copies a file from repo to source."""

    # Given
    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()
    fragments_dir = repo / "fragments" / "test_fragment_1"
    fragments_dir.mkdir(parents=True)
    (fragments_dir / ".testrc").write_text("applied_content")

    (repo / "fragments.toml").write_text(f'''
[test_fragment_1]
targets = [{{ src = "{home}/.testrc" }}]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--apply"])

    # When
    main()
    output = capsys.readouterr().out

    # Then
    applied = home / ".testrc"
    assert applied.exists()
    assert applied.read_text() == "applied_content"

    assert (
        f'''Performing apply for test_fragment_1 fragments.
Copying "./fragments/test_fragment_1/.testrc" to "{home}/.testrc"...  Done.
'''
        == output
    )


def test_apply_copies_directory_to_system(tmp_path, monkeypatch, capsys):
    """--apply copies a directory from repo to source."""

    # Given
    home = tmp_path / "home"
    home.mkdir()
    (home / ".config").mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()
    fragments_dir = repo / "fragments" / "test_fragment_1" / "testapp"
    fragments_dir.mkdir(parents=True)
    (fragments_dir / "settings.json").write_text('{"applied": true}')
    (fragments_dir / "subdir").mkdir()
    (fragments_dir / "subdir" / "nested.txt").write_text("nested_applied")

    (repo / "fragments.toml").write_text(f'''
[test_fragment_1]
targets = [{{ src = "{home}/.config/testapp" }}]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--apply"])

    # When
    main()
    output = capsys.readouterr().out

    # Then
    applied_dir = home / ".config" / "testapp"
    assert applied_dir.is_dir()
    assert (applied_dir / "settings.json").read_text() == '{"applied": true}'
    assert (applied_dir / "subdir" / "nested.txt").read_text() == "nested_applied"

    assert (
        f'''Performing apply for test_fragment_1 fragments.
Copying "./fragments/test_fragment_1/testapp" to "{home}/.config/testapp"...  Done.
'''
        == output
    )


def test_apply_all_fragments(tmp_path, monkeypatch, capsys):
    """--apply without --select applies all fragments."""

    # Given
    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()

    frag1 = repo / "fragments" / "test_fragment_1"
    frag1.mkdir(parents=True)
    (frag1 / ".config1").write_text("applied1")

    frag2 = repo / "fragments" / "test_fragment_2"
    frag2.mkdir(parents=True)
    (frag2 / ".config2").write_text("applied2")

    (repo / "fragments.toml").write_text(f'''
[test_fragment_1]
targets = [{{ src = "{home}/.config1" }}]

[test_fragment_2]
targets = [{{ src = "{home}/.config2" }}]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--apply"])

    # When
    main()
    output = capsys.readouterr().out

    # Then
    assert (home / ".config1").read_text() == "applied1"
    assert (home / ".config2").read_text() == "applied2"

    assert (
        f'''Performing apply for test_fragment_1, test_fragment_2 fragments.
Copying "./fragments/test_fragment_1/.config1" to "{home}/.config1"...  Done.
Copying "./fragments/test_fragment_2/.config2" to "{home}/.config2"...  Done.
'''
        == output
    )


def test_apply_with_dir_option(tmp_path, monkeypatch, capsys):
    """--apply with dir option reads from subdirectory."""

    # Given
    home = tmp_path / "home"
    home.mkdir()
    (home / ".config").mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()
    fragments_dir = repo / "fragments" / "test_fragment_1" / "dotconfig" / "testapp"
    fragments_dir.mkdir(parents=True)
    (fragments_dir / "config.toml").write_text("applied_setting = true")

    (repo / "fragments.toml").write_text(f'''
[test_fragment_1]
targets = [{{ src = "{home}/.config/testapp", dir = "dotconfig" }}]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--apply"])

    # When
    main()
    output = capsys.readouterr().out

    # Then
    applied = home / ".config" / "testapp" / "config.toml"
    assert applied.exists()
    assert applied.read_text() == "applied_setting = true"

    assert (
        f'''Performing apply for test_fragment_1 fragments.
Copying "./fragments/test_fragment_1/dotconfig/testapp" to "{home}/.config/testapp"...  Done.
'''
        == output
    )


def test_apply_skips_nonexistent_source(tmp_path, monkeypatch, capsys):
    """--apply skips files that don't exist in repo."""

    # Given
    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "fragments" / "test_fragment_1").mkdir(parents=True)

    (repo / "fragments.toml").write_text(f'''
[test_fragment_1]
targets = [{{ src = "{home}/.testrc" }}]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--apply"])

    # When
    main()
    output = capsys.readouterr().out

    # Then
    assert not (home / ".testrc").exists()

    assert (
        f'''Performing apply for test_fragment_1 fragments.
Copying "./fragments/test_fragment_1/.testrc" to "{home}/.testrc"...  Skipped...
'''
        == output
    )


def test_apply_with_select_single_fragment(tmp_path, monkeypatch, capsys):
    """--apply --select applies only specified fragment."""

    # Given
    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()

    frag1 = repo / "fragments" / "test_fragment_1"
    frag1.mkdir(parents=True)
    (frag1 / ".config1").write_text("applied1")

    frag2 = repo / "fragments" / "test_fragment_2"
    frag2.mkdir(parents=True)
    (frag2 / ".config2").write_text("applied2")

    (repo / "fragments.toml").write_text(f'''
[test_fragment_1]
targets = [{{ src = "{home}/.config1" }}]

[test_fragment_2]
targets = [{{ src = "{home}/.config2" }}]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(
        sys, "argv", ["nastrajacz", "--apply", "--select", "test_fragment_1"]
    )

    # When
    main()
    output = capsys.readouterr().out

    # Then
    assert (home / ".config1").read_text() == "applied1"
    assert not (home / ".config2").exists()

    assert (
        f'''Performing apply for test_fragment_1 fragments.
Copying "./fragments/test_fragment_1/.config1" to "{home}/.config1"...  Done.
'''
        == output
    )


def test_apply_with_select_multiple_fragments(tmp_path, monkeypatch, capsys):
    """--apply --select with comma-separated list applies only specified fragments."""

    # Given
    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()

    frag1 = repo / "fragments" / "test_fragment_1"
    frag1.mkdir(parents=True)
    (frag1 / ".config1").write_text("applied1")

    frag2 = repo / "fragments" / "test_fragment_2"
    frag2.mkdir(parents=True)
    (frag2 / ".config2").write_text("applied2")

    frag3 = repo / "fragments" / "test_fragment_3"
    frag3.mkdir(parents=True)
    (frag3 / ".config3").write_text("applied3")

    (repo / "fragments.toml").write_text(f'''
[test_fragment_1]
targets = [{{ src = "{home}/.config1" }}]

[test_fragment_2]
targets = [{{ src = "{home}/.config2" }}]

[test_fragment_3]
targets = [{{ src = "{home}/.config3" }}]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(
        sys,
        "argv",
        ["nastrajacz", "--apply", "--select", "test_fragment_1,test_fragment_3"],
    )

    # When
    main()
    output = capsys.readouterr().out

    # Then
    assert (home / ".config1").read_text() == "applied1"
    assert not (home / ".config2").exists()
    assert (home / ".config3").read_text() == "applied3"

    assert (
        f'''Performing apply for test_fragment_1, test_fragment_3 fragments.
Copying "./fragments/test_fragment_1/.config1" to "{home}/.config1"...  Done.
Copying "./fragments/test_fragment_3/.config3" to "{home}/.config3"...  Done.
'''
        == output
    )


def test_apply_creates_missing_parent_directories(tmp_path, monkeypatch, capsys):
    """--apply creates parent directories when they don't exist."""

    # Given
    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()
    fragments_dir = repo / "fragments" / "test_fragment_1" / "testapp"
    fragments_dir.mkdir(parents=True)
    (fragments_dir / "settings.json").write_text('{"applied": true}')

    (repo / "fragments.toml").write_text(f'''
[test_fragment_1]
targets = [{{ src = "{home}/.config/testapp" }}]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--apply"])

    # When
    main()
    output = capsys.readouterr().out

    # Then
    applied_dir = home / ".config" / "testapp"
    assert applied_dir.is_dir()
    assert (applied_dir / "settings.json").read_text() == '{"applied": true}'

    assert (
        f'''Performing apply for test_fragment_1 fragments.
Copying "./fragments/test_fragment_1/testapp" to "{home}/.config/testapp"...  Done.
'''
        == output
    )
