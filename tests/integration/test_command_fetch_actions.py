import sys

from src.nastrajacz import main


def test_fetch_runs_after_fetch_script_in_fragment_directory(
    tmp_path, monkeypatch, terminal
):
    """--fetch runs after_fetch script after copying files, in the fragment directory."""

    # Given
    home = tmp_path / "home"
    home.mkdir()
    (home / ".testrc").write_text("fetched_content")

    repo = tmp_path / "repo"
    repo.mkdir()
    fragments_dir = repo / "fragments" / "test_fragment_1"
    fragments_dir.mkdir(parents=True)

    (repo / "fragments.toml").write_text(f'''
[test_fragment_1]
targets = [{{ src = "{home}/.testrc" }}]

[test_fragment_1.actions]
after_fetch = "pwd > cwd.txt"
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--fetch"])

    # When
    main()
    terminal.render()

    # Then
    assert (fragments_dir / ".testrc").read_text() == "fetched_content"

    cwd_marker = fragments_dir / "cwd.txt"
    assert cwd_marker.exists(), "after_fetch script did not run"

    assert cwd_marker.read_text().strip() == str(fragments_dir)

    terminal.assert_lines(
        [
            "Performing fetch for test_fragment_1 fragments.",
            "",
            "Processing fragment test_fragment_1.",
            f'Copying "{home}/.testrc" to "./fragments/test_fragment_1" [ DONE].',
            "Running after_fetch for test_fragment_1 [ DONE] (exit code 0).",
            "Finished processing fragment test_fragment_1 [ DONE].",
        ]
    )


def test_fetch_does_not_run_after_fetch_when_not_defined_or_empty(
    tmp_path, monkeypatch, capsys
):
    """--fetch does not run after_fetch when actions section is missing or after_fetch is empty."""

    # Given
    home = tmp_path / "home"
    home.mkdir()
    (home / ".config1").write_text("content1")
    (home / ".config2").write_text("content2")

    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "fragments.toml").write_text(f'''
[no_actions_fragment]
targets = [{{ src = "{home}/.config1" }}]

[empty_after_fetch_fragment]
targets = [{{ src = "{home}/.config2" }}]

[empty_after_fetch_fragment.actions]
after_fetch = ""
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--fetch"])

    # When
    main()
    output = capsys.readouterr().out

    # Then
    frag1 = repo / "fragments" / "no_actions_fragment"
    frag2 = repo / "fragments" / "empty_after_fetch_fragment"

    assert (frag1 / ".config1").read_text() == "content1"
    assert (frag2 / ".config2").read_text() == "content2"

    assert not (frag1 / "cwd.txt").exists()
    assert not (frag2 / "cwd.txt").exists()
    assert "Running after_fetch" not in output


def test_fetch_prints_warning_when_after_fetch_script_fails(
    tmp_path, monkeypatch, capsys
):
    """--fetch prints warning when after_fetch script fails but continues with other fragments."""

    # Given
    home = tmp_path / "home"
    home.mkdir()
    (home / ".config1").write_text("content1")
    (home / ".config2").write_text("content2")

    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "fragments.toml").write_text(f'''
[failing_fragment]
targets = [{{ src = "{home}/.config1" }}]

[failing_fragment.actions]
after_fetch = "exit 1"

[succeeding_fragment]
targets = [{{ src = "{home}/.config2" }}]

[succeeding_fragment.actions]
after_fetch = "touch success_marker.txt"
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--fetch"])

    # When
    main()
    output = capsys.readouterr().out

    # Then
    frag1 = repo / "fragments" / "failing_fragment"
    frag2 = repo / "fragments" / "succeeding_fragment"

    assert (frag1 / ".config1").read_text() == "content1"
    assert (frag2 / ".config2").read_text() == "content2"

    assert "failing_fragment" in output
    assert "warning" in output.lower() or "failed" in output.lower()

    assert (frag2 / "success_marker.txt").exists()


def test_fetch_after_fetch_runs_for_each_selected_fragment(
    tmp_path, monkeypatch, terminal
):
    """--fetch runs after_fetch for each selected fragment independently."""

    # Given
    home = tmp_path / "home"
    home.mkdir()
    (home / ".config_a").write_text("content_a")
    (home / ".config_b").write_text("content_b")

    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "fragments.toml").write_text(f'''
[fragment_a]
targets = [{{ src = "{home}/.config_a" }}]

[fragment_a.actions]
after_fetch = "touch marker_a.txt"

[fragment_b]
targets = [{{ src = "{home}/.config_b" }}]

[fragment_b.actions]
after_fetch = "touch marker_b.txt"
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--fetch"])

    # When
    main()
    terminal.render()

    # Then
    frag1 = repo / "fragments" / "fragment_a"
    frag2 = repo / "fragments" / "fragment_b"

    assert (frag1 / ".config_a").read_text() == "content_a"
    assert (frag2 / ".config_b").read_text() == "content_b"

    assert (frag1 / "marker_a.txt").exists(), "after_fetch for fragment_a did not run"
    assert (frag2 / "marker_b.txt").exists(), "after_fetch for fragment_b did not run"

    terminal.assert_lines(
        [
            "Performing fetch for fragment_a, fragment_b fragments.",
            "",
            "Processing fragment fragment_a.",
            f'Copying "{home}/.config_a" to "./fragments/fragment_a" [ DONE].',
            "Running after_fetch for fragment_a [ DONE] (exit code 0).",
            "Finished processing fragment fragment_a [ DONE].",
            "",
            "Processing fragment fragment_b.",
            f'Copying "{home}/.config_b" to "./fragments/fragment_b" [ DONE].',
            "Running after_fetch for fragment_b [ DONE] (exit code 0).",
            "Finished processing fragment fragment_b [ DONE].",
        ]
    )


def test_fetch_runs_before_fetch_script_in_fragment_directory(
    tmp_path, monkeypatch, terminal
):
    """--fetch runs before_fetch script before copying files, in the fragment directory."""

    # Given
    home = tmp_path / "home"
    home.mkdir()
    (home / ".testrc").write_text("fetched_content")

    repo = tmp_path / "repo"
    repo.mkdir()
    fragments_dir = repo / "fragments" / "test_fragment_1"
    fragments_dir.mkdir(parents=True)

    (repo / "fragments.toml").write_text(f'''
[test_fragment_1]
targets = [{{ src = "{home}/.testrc" }}]

[test_fragment_1.actions]
before_fetch = "pwd > cwd.txt && echo before > order.txt"
after_fetch = "echo after >> order.txt"
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--fetch"])

    # When
    main()
    terminal.render()

    # Then
    assert (fragments_dir / ".testrc").read_text() == "fetched_content"

    cwd_marker = fragments_dir / "cwd.txt"
    assert cwd_marker.exists(), "before_fetch script did not run"
    assert cwd_marker.read_text().strip() == str(fragments_dir)

    order_marker = fragments_dir / "order.txt"
    assert order_marker.exists()
    assert order_marker.read_text() == "before\nafter\n"

    terminal.assert_lines(
        [
            "Performing fetch for test_fragment_1 fragments.",
            "",
            "Processing fragment test_fragment_1.",
            "Running before_fetch for test_fragment_1 [ DONE] (exit code 0).",
            f'Copying "{home}/.testrc" to "./fragments/test_fragment_1" [ DONE].',
            "Running after_fetch for test_fragment_1 [ DONE] (exit code 0).",
            "Finished processing fragment test_fragment_1 [ DONE].",
        ]
    )


def test_fetch_does_not_run_before_fetch_when_not_defined_or_empty(
    tmp_path, monkeypatch, capsys
):
    """--fetch does not run before_fetch when actions section is missing or before_fetch is empty."""

    # Given
    home = tmp_path / "home"
    home.mkdir()
    (home / ".config1").write_text("content1")
    (home / ".config2").write_text("content2")

    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "fragments.toml").write_text(f'''
[no_actions_fragment]
targets = [{{ src = "{home}/.config1" }}]

[empty_before_fetch_fragment]
targets = [{{ src = "{home}/.config2" }}]

[empty_before_fetch_fragment.actions]
before_fetch = ""
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--fetch"])

    # When
    main()
    output = capsys.readouterr().out

    # Then
    frag1 = repo / "fragments" / "no_actions_fragment"
    frag2 = repo / "fragments" / "empty_before_fetch_fragment"

    assert (frag1 / ".config1").read_text() == "content1"
    assert (frag2 / ".config2").read_text() == "content2"

    assert not (frag1 / "marker.txt").exists()
    assert not (frag2 / "marker.txt").exists()
    assert "Running before_fetch" not in output


def test_fetch_skips_fragment_when_before_fetch_fails(tmp_path, monkeypatch, capsys):
    """--fetch skips copying and after_fetch when before_fetch fails, continues with other fragments."""

    # Given
    home = tmp_path / "home"
    home.mkdir()
    (home / ".config1").write_text("content1")
    (home / ".config2").write_text("content2")

    repo = tmp_path / "repo"
    repo.mkdir()

    # Pre-create fragment directories so before_fetch can run
    frag1 = repo / "fragments" / "failing_fragment"
    frag1.mkdir(parents=True)
    frag2 = repo / "fragments" / "succeeding_fragment"
    frag2.mkdir(parents=True)

    (repo / "fragments.toml").write_text(f'''
[failing_fragment]
targets = [{{ src = "{home}/.config1" }}]

[failing_fragment.actions]
before_fetch = "exit 1"
after_fetch = "touch after_marker.txt"

[succeeding_fragment]
targets = [{{ src = "{home}/.config2" }}]

[succeeding_fragment.actions]
before_fetch = "touch before_marker.txt"
after_fetch = "touch after_marker.txt"
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--fetch"])

    # When
    main()
    output = capsys.readouterr().out

    # Then
    assert not (frag1 / ".config1").exists(), (
        "File should not be copied when before_fetch fails"
    )
    assert not (frag1 / "after_marker.txt").exists(), (
        "after_fetch should not run when before_fetch fails"
    )

    assert (frag2 / ".config2").read_text() == "content2"
    assert (frag2 / "before_marker.txt").exists()
    assert (frag2 / "after_marker.txt").exists()

    assert "failing_fragment" in output
    assert "warning" in output.lower() or "failed" in output.lower()


def test_fetch_before_fetch_runs_for_each_selected_fragment(
    tmp_path, monkeypatch, terminal
):
    """--fetch runs before_fetch for each selected fragment independently."""

    # Given
    home = tmp_path / "home"
    home.mkdir()
    (home / ".config_a").write_text("content_a")
    (home / ".config_b").write_text("content_b")

    repo = tmp_path / "repo"
    repo.mkdir()

    frag1 = repo / "fragments" / "fragment_a"
    frag2 = repo / "fragments" / "fragment_b"

    (repo / "fragments.toml").write_text(f'''
[fragment_a]
targets = [{{ src = "{home}/.config_a" }}]

[fragment_a.actions]
before_fetch = "touch marker_a.txt"

[fragment_b]
targets = [{{ src = "{home}/.config_b" }}]

[fragment_b.actions]
before_fetch = "touch marker_b.txt"
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--fetch"])

    # When
    main()
    terminal.render()

    # Then
    assert (frag1 / ".config_a").read_text() == "content_a"
    assert (frag2 / ".config_b").read_text() == "content_b"

    assert (frag1 / "marker_a.txt").exists(), "before_fetch for fragment_a did not run"
    assert (frag2 / "marker_b.txt").exists(), "before_fetch for fragment_b did not run"

    terminal.assert_lines(
        [
            "Performing fetch for fragment_a, fragment_b fragments.",
            "",
            "Processing fragment fragment_a.",
            "Running before_fetch for fragment_a [ DONE] (exit code 0).",
            f'Copying "{home}/.config_a" to "./fragments/fragment_a" [ DONE].',
            "Finished processing fragment fragment_a [ DONE].",
            "",
            "Processing fragment fragment_b.",
            "Running before_fetch for fragment_b [ DONE] (exit code 0).",
            f'Copying "{home}/.config_b" to "./fragments/fragment_b" [ DONE].',
            "Finished processing fragment fragment_b [ DONE].",
        ]
    )
