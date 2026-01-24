import sys

from src.nastrajacz import main


def test_apply_runs_after_apply_script_in_fragment_directory(
    tmp_path, monkeypatch, capsys
):
    """--apply runs after_apply script after copying files, in the fragment directory."""

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

[test_fragment_1.actions]
after_apply = "pwd > cwd.txt"
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--apply"])

    # When
    main()
    output = capsys.readouterr().out

    # Then
    assert (home / ".testrc").read_text() == "applied_content"

    cwd_marker = fragments_dir / "cwd.txt"
    assert cwd_marker.exists(), "after_apply script did not run"

    assert cwd_marker.read_text().strip() == str(fragments_dir)

    assert "Running after_apply for test_fragment_1" in output


def test_apply_does_not_run_after_apply_when_not_defined_or_empty(
    tmp_path, monkeypatch, capsys
):
    """--apply does not run after_apply when actions section is missing or after_apply is empty."""

    # Given
    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()

    frag1 = repo / "fragments" / "no_actions_fragment"
    frag1.mkdir(parents=True)
    (frag1 / ".config1").write_text("content1")

    frag2 = repo / "fragments" / "empty_after_apply_fragment"
    frag2.mkdir(parents=True)
    (frag2 / ".config2").write_text("content2")

    (repo / "fragments.toml").write_text(f'''
[no_actions_fragment]
targets = [{{ src = "{home}/.config1" }}]

[empty_after_apply_fragment]
targets = [{{ src = "{home}/.config2" }}]

[empty_after_apply_fragment.actions]
after_apply = ""
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--apply"])

    # When
    main()
    output = capsys.readouterr().out

    # Then
    assert (home / ".config1").read_text() == "content1"
    assert (home / ".config2").read_text() == "content2"

    assert not (frag1 / "cwd.txt").exists()
    assert not (frag2 / "cwd.txt").exists()
    assert "Running after_apply" not in output


def test_apply_prints_warning_when_after_apply_script_fails(
    tmp_path, monkeypatch, capsys
):
    """--apply prints warning when after_apply script fails but continues with other fragments."""

    # Given
    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()

    frag1 = repo / "fragments" / "failing_fragment"
    frag1.mkdir(parents=True)
    (frag1 / ".config1").write_text("content1")

    frag2 = repo / "fragments" / "succeeding_fragment"
    frag2.mkdir(parents=True)
    (frag2 / ".config2").write_text("content2")

    (repo / "fragments.toml").write_text(f'''
[failing_fragment]
targets = [{{ src = "{home}/.config1" }}]

[failing_fragment.actions]
after_apply = "exit 1"

[succeeding_fragment]
targets = [{{ src = "{home}/.config2" }}]

[succeeding_fragment.actions]
after_apply = "touch success_marker.txt"
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--apply"])

    # When
    main()
    output = capsys.readouterr().out

    # Then
    assert (home / ".config1").read_text() == "content1"
    assert (home / ".config2").read_text() == "content2"

    # TODO: More specific assertions on output.
    assert "failing_fragment" in output
    assert "warning" in output.lower() or "failed" in output.lower()

    assert (frag2 / "success_marker.txt").exists()


def test_apply_after_apply_runs_for_each_selected_fragment(
    tmp_path, monkeypatch, capsys
):
    """--apply runs after_apply for each selected fragment independently."""

    # Given
    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()

    frag1 = repo / "fragments" / "fragment_a"
    frag1.mkdir(parents=True)
    (frag1 / ".config_a").write_text("content_a")

    frag2 = repo / "fragments" / "fragment_b"
    frag2.mkdir(parents=True)
    (frag2 / ".config_b").write_text("content_b")

    (repo / "fragments.toml").write_text(f'''
[fragment_a]
targets = [{{ src = "{home}/.config_a" }}]

[fragment_a.actions]
after_apply = "touch marker_a.txt"

[fragment_b]
targets = [{{ src = "{home}/.config_b" }}]

[fragment_b.actions]
after_apply = "touch marker_b.txt"
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--apply"])

    # When
    main()
    output = capsys.readouterr().out

    # Then
    assert (home / ".config_a").read_text() == "content_a"
    assert (home / ".config_b").read_text() == "content_b"

    assert (frag1 / "marker_a.txt").exists(), "after_apply for fragment_a did not run"
    assert (frag2 / "marker_b.txt").exists(), "after_apply for fragment_b did not run"

    assert "Running after_apply for fragment_a" in output
    assert "Running after_apply for fragment_b" in output
