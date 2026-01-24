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


def test_apply_runs_before_apply_script_in_fragment_directory(
    tmp_path, monkeypatch, capsys
):
    """--apply runs before_apply script before copying files, in the fragment directory."""

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
before_apply = "pwd > cwd.txt && echo before > order.txt"
after_apply = "echo after >> order.txt"
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--apply"])

    # When
    main()
    output = capsys.readouterr().out

    # Then
    assert (home / ".testrc").read_text() == "applied_content"

    cwd_marker = fragments_dir / "cwd.txt"
    assert cwd_marker.exists(), "before_apply script did not run"
    assert cwd_marker.read_text().strip() == str(fragments_dir)

    order_marker = fragments_dir / "order.txt"
    assert order_marker.exists()
    assert order_marker.read_text() == "before\nafter\n"

    assert "Running before_apply for test_fragment_1" in output
    assert "Running after_apply for test_fragment_1" in output


def test_apply_does_not_run_before_apply_when_not_defined_or_empty(
    tmp_path, monkeypatch, capsys
):
    """--apply does not run before_apply when actions section is missing or before_apply is empty."""

    # Given
    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()

    frag1 = repo / "fragments" / "no_actions_fragment"
    frag1.mkdir(parents=True)
    (frag1 / ".config1").write_text("content1")

    frag2 = repo / "fragments" / "empty_before_apply_fragment"
    frag2.mkdir(parents=True)
    (frag2 / ".config2").write_text("content2")

    (repo / "fragments.toml").write_text(f'''
[no_actions_fragment]
targets = [{{ src = "{home}/.config1" }}]

[empty_before_apply_fragment]
targets = [{{ src = "{home}/.config2" }}]

[empty_before_apply_fragment.actions]
before_apply = ""
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--apply"])

    # When
    main()
    output = capsys.readouterr().out

    # Then
    assert (home / ".config1").read_text() == "content1"
    assert (home / ".config2").read_text() == "content2"

    assert not (frag1 / "marker.txt").exists()
    assert not (frag2 / "marker.txt").exists()
    assert "Running before_apply" not in output


def test_apply_skips_fragment_when_before_apply_fails(tmp_path, monkeypatch, capsys):
    """--apply skips copying and after_apply when before_apply fails, continues with other fragments."""

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
before_apply = "exit 1"
after_apply = "touch after_marker.txt"

[succeeding_fragment]
targets = [{{ src = "{home}/.config2" }}]

[succeeding_fragment.actions]
before_apply = "touch before_marker.txt"
after_apply = "touch after_marker.txt"
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--apply"])

    # When
    main()
    output = capsys.readouterr().out

    # Then
    assert not (home / ".config1").exists(), (
        "File should not be copied when before_apply fails"
    )
    assert not (frag1 / "after_marker.txt").exists(), (
        "after_apply should not run when before_apply fails"
    )

    assert (home / ".config2").read_text() == "content2"
    assert (frag2 / "before_marker.txt").exists()
    assert (frag2 / "after_marker.txt").exists()

    assert "failing_fragment" in output
    assert "warning" in output.lower() or "failed" in output.lower()


def test_apply_before_apply_runs_for_each_selected_fragment(
    tmp_path, monkeypatch, capsys
):
    """--apply runs before_apply for each selected fragment independently."""

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
before_apply = "touch marker_a.txt"

[fragment_b]
targets = [{{ src = "{home}/.config_b" }}]

[fragment_b.actions]
before_apply = "touch marker_b.txt"
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--apply"])

    # When
    main()
    output = capsys.readouterr().out

    # Then
    assert (home / ".config_a").read_text() == "content_a"
    assert (home / ".config_b").read_text() == "content_b"

    assert (frag1 / "marker_a.txt").exists(), "before_apply for fragment_a did not run"
    assert (frag2 / "marker_b.txt").exists(), "before_apply for fragment_b did not run"

    assert "Running before_apply for fragment_a" in output
    assert "Running before_apply for fragment_b" in output
