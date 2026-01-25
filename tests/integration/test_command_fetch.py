import sys

from src.nastrajacz import main


def test_fetch_copies_single_file_to_fragments_dir(tmp_path, monkeypatch, terminal):
    """--fetch copies a file from source to repo."""

    # Given
    home = tmp_path / "home"
    home.mkdir()
    (home / ".testrc").write_text("config_content")

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "fragments.toml").write_text(f'''
[test_fragment_1]
targets = [{{ src = "{home}/.testrc" }}]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--fetch"])

    # When
    main()
    terminal.render()

    # Then
    fetched = repo / "fragments" / "test_fragment_1" / ".testrc"
    assert fetched.exists()
    assert fetched.read_text() == "config_content"

    terminal.assert_lines(
        [
            "Performing fetch for test_fragment_1 fragments.",
            "",
            "Processing fragment test_fragment_1.",
            f'Copying "{home}/.testrc" to "./fragments/test_fragment_1" [ DONE].',
            "Finished processing fragment test_fragment_1 [ DONE].",
        ]
    )


def test_fetch_copies_directory_to_fragments_dir(tmp_path, monkeypatch, terminal):
    """--fetch copies a directory recursively to repo."""

    # Given
    home = tmp_path / "home"
    home.mkdir()
    config_dir = home / ".config" / "testapp"
    config_dir.mkdir(parents=True)
    (config_dir / "settings.json").write_text('{"key": "value"}')
    (config_dir / "subdir").mkdir()
    (config_dir / "subdir" / "nested.txt").write_text("nested_content")

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "fragments.toml").write_text(f'''
[test_fragment_1]
targets = [{{ src = "{config_dir}" }}]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--fetch"])

    # When
    main()
    terminal.render()

    # Then
    fetched_dir = repo / "fragments" / "test_fragment_1" / "testapp"
    assert fetched_dir.is_dir()
    assert (fetched_dir / "settings.json").read_text() == '{"key": "value"}'
    assert (fetched_dir / "subdir" / "nested.txt").read_text() == "nested_content"

    terminal.assert_lines(
        [
            "Performing fetch for test_fragment_1 fragments.",
            "",
            "Processing fragment test_fragment_1.",
            f'Copying "{config_dir}" to "./fragments/test_fragment_1/testapp" [ DONE].',
            "Finished processing fragment test_fragment_1 [ DONE].",
        ]
    )


def test_fetch_multiple_targets_in_fragment(tmp_path, monkeypatch, terminal):
    """--fetch handles multiple targets within a single fragment."""

    # Given
    home = tmp_path / "home"
    home.mkdir()
    (home / ".file1").write_text("content1")
    (home / ".file2").write_text("content2")

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "fragments.toml").write_text(f'''
[test_fragment_1]
targets = [
    {{ src = "{home}/.file1" }},
    {{ src = "{home}/.file2" }},
]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--fetch"])

    # When
    main()
    terminal.render()

    # Then
    assert (repo / "fragments" / "test_fragment_1" / ".file1").read_text() == "content1"
    assert (repo / "fragments" / "test_fragment_1" / ".file2").read_text() == "content2"

    terminal.assert_lines(
        [
            "Performing fetch for test_fragment_1 fragments.",
            "",
            "Processing fragment test_fragment_1.",
            f'Copying "{home}/.file1" to "./fragments/test_fragment_1" [ DONE].',
            f'Copying "{home}/.file2" to "./fragments/test_fragment_1" [ DONE].',
            "Finished processing fragment test_fragment_1 [ DONE].",
        ]
    )


def test_fetch_all_fragments(tmp_path, monkeypatch, terminal):
    """--fetch without --select fetches all fragments."""
    # Given
    home = tmp_path / "home"
    home.mkdir()
    (home / ".config1").write_text("config1")
    (home / ".config2").write_text("config2")

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "fragments.toml").write_text(f'''
[test_fragment_1]
targets = [{{ src = "{home}/.config1" }}]

[test_fragment_2]
targets = [{{ src = "{home}/.config2" }}]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--fetch"])

    # When
    main()
    terminal.render()

    # Then
    assert (
        repo / "fragments" / "test_fragment_1" / ".config1"
    ).read_text() == "config1"
    assert (
        repo / "fragments" / "test_fragment_2" / ".config2"
    ).read_text() == "config2"

    terminal.assert_lines(
        [
            "Performing fetch for test_fragment_1, test_fragment_2 fragments.",
            "",
            "Processing fragment test_fragment_1.",
            f'Copying "{home}/.config1" to "./fragments/test_fragment_1" [ DONE].',
            "Finished processing fragment test_fragment_1 [ DONE].",
            "",
            "Processing fragment test_fragment_2.",
            f'Copying "{home}/.config2" to "./fragments/test_fragment_2" [ DONE].',
            "Finished processing fragment test_fragment_2 [ DONE].",
        ]
    )


def test_fetch_with_dir_option_creates_subdir(tmp_path, monkeypatch, terminal):
    """--fetch with dir option places files in subdirectory."""

    # Given
    home = tmp_path / "home"
    home.mkdir()
    config_dir = home / ".config" / "testapp"
    config_dir.mkdir(parents=True)
    (config_dir / "config.toml").write_text("setting = true")

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "fragments.toml").write_text(f'''
[test_fragment_1]
targets = [{{ src = "{config_dir}", dir = "dotconfig" }}]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--fetch"])

    # When
    main()
    terminal.render()

    # Then
    fetched = (
        repo / "fragments" / "test_fragment_1" / "dotconfig" / "testapp" / "config.toml"
    )
    assert fetched.exists()
    assert fetched.read_text() == "setting = true"

    terminal.assert_lines(
        [
            "Performing fetch for test_fragment_1 fragments.",
            "",
            "Processing fragment test_fragment_1.",
            f'Copying "{config_dir}" to "./fragments/test_fragment_1/dotconfig/testapp" [ DONE].',
            "Finished processing fragment test_fragment_1 [ DONE].",
        ]
    )


def test_fetch_skips_nonexistent_source(tmp_path, monkeypatch, terminal):
    """--fetch skips files that don't exist at source location."""

    # Given
    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "fragments.toml").write_text(f'''
[test_fragment_1]
targets = [{{ src = "{home}/.nonexistent" }}]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--fetch"])

    # When
    main()
    terminal.render()

    # Then
    terminal.assert_lines(
        [
            "Performing fetch for test_fragment_1 fragments.",
            "",
            "Processing fragment test_fragment_1.",
            f'Copying "{home}/.nonexistent" to "./fragments/test_fragment_1" [ SKIP].',
            "Finished processing fragment test_fragment_1 [ DONE].",
        ]
    )


def test_fetch_with_select_single_fragment(tmp_path, monkeypatch, terminal):
    """--fetch --select fetches only specified fragment."""

    # Given
    home = tmp_path / "home"
    home.mkdir()
    (home / ".config1").write_text("config1")
    (home / ".config2").write_text("config2")

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "fragments.toml").write_text(f'''
[test_fragment_1]
targets = [{{ src = "{home}/.config1" }}]

[test_fragment_2]
targets = [{{ src = "{home}/.config2" }}]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(
        sys, "argv", ["nastrajacz", "--fetch", "--select", "test_fragment_1"]
    )

    # When
    main()
    terminal.render()

    # Then
    assert (repo / "fragments" / "test_fragment_1" / ".config1").exists()
    assert not (repo / "fragments" / "test_fragment_2").exists()

    terminal.assert_lines(
        [
            "Performing fetch for test_fragment_1 fragments.",
            "",
            "Processing fragment test_fragment_1.",
            f'Copying "{home}/.config1" to "./fragments/test_fragment_1" [ DONE].',
            "Finished processing fragment test_fragment_1 [ DONE].",
        ]
    )


def test_fetch_with_select_multiple_fragments(tmp_path, monkeypatch, terminal):
    """--fetch --select with comma-separated list fetches specified fragments."""

    # Given
    home = tmp_path / "home"
    home.mkdir()
    (home / ".config1").write_text("config1")
    (home / ".config2").write_text("config2")
    (home / ".config3").write_text("config3")

    repo = tmp_path / "repo"
    repo.mkdir()
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
        ["nastrajacz", "--fetch", "--select", "test_fragment_1,test_fragment_3"],
    )

    # When
    main()
    terminal.render()

    # Then
    assert (repo / "fragments" / "test_fragment_1" / ".config1").exists()
    assert not (repo / "fragments" / "test_fragment_2").exists()
    assert (repo / "fragments" / "test_fragment_3" / ".config3").exists()

    terminal.assert_lines(
        [
            "Performing fetch for test_fragment_1, test_fragment_3 fragments.",
            "",
            "Processing fragment test_fragment_1.",
            f'Copying "{home}/.config1" to "./fragments/test_fragment_1" [ DONE].',
            "Finished processing fragment test_fragment_1 [ DONE].",
            "",
            "Processing fragment test_fragment_3.",
            f'Copying "{home}/.config3" to "./fragments/test_fragment_3" [ DONE].',
            "Finished processing fragment test_fragment_3 [ DONE].",
        ]
    )
