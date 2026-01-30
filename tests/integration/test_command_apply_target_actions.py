import sys

from src.nastrajacz import main


def test_apply_runs_after_apply_target_action_in_fragment_directory(
    tmp_path, monkeypatch, terminal
):
    """--apply runs target's after_apply action after copying the target file."""

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
targets = [{{ src = "{home}/.testrc", actions = {{ after_apply = "pwd > cwd.txt" }} }}]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--apply"])

    # When
    main()
    terminal.render()

    # Then
    assert (home / ".testrc").read_text() == "applied_content"

    cwd_marker = fragments_dir / "cwd.txt"
    assert cwd_marker.exists(), "target after_apply action did not run"
    assert cwd_marker.read_text().strip() == str(fragments_dir)

    terminal.assert_lines(
        [
            "Performing apply for test_fragment_1 fragments.",
            "",
            "Processing fragment test_fragment_1.",
            f'Copying "./fragments/test_fragment_1/.testrc" to "{home}/.testrc" [ DONE].',
            "Running after_apply for test_fragment_1/.testrc [ DONE] (exit code 0).",
            "Finished processing fragment test_fragment_1 [ DONE].",
        ]
    )


def test_apply_does_not_run_target_after_apply_when_not_defined_or_empty(
    tmp_path, monkeypatch, terminal
):
    """--apply does not run target's after_apply when not defined or empty."""

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
targets = [{{ src = "{home}/.config2", actions = {{ after_apply = "" }} }}]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--apply"])

    # When
    main()
    terminal.render()

    # Then
    assert (home / ".config1").read_text() == "content1"
    assert (home / ".config2").read_text() == "content2"

    assert not (frag1 / "cwd.txt").exists()
    assert not (frag2 / "cwd.txt").exists()

    terminal.assert_lines(
        [
            "Performing apply for empty_after_apply_fragment, no_actions_fragment fragments.",
            "",
            "Processing fragment empty_after_apply_fragment.",
            f'Copying "./fragments/empty_after_apply_fragment/.config2" to "{home}/.config2" [ DONE].',
            "Finished processing fragment empty_after_apply_fragment [ DONE].",
            "",
            "Processing fragment no_actions_fragment.",
            f'Copying "./fragments/no_actions_fragment/.config1" to "{home}/.config1" [ DONE].',
            "Finished processing fragment no_actions_fragment [ DONE].",
        ]
    )


def test_apply_prints_warning_when_target_after_apply_fails(
    tmp_path, monkeypatch, terminal
):
    """--apply prints warning when target's after_apply fails but continues with other targets."""

    # Given
    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()

    frag = repo / "fragments" / "test_fragment"
    frag.mkdir(parents=True)
    (frag / ".config1").write_text("content1")
    (frag / ".config2").write_text("content2")

    (repo / "fragments.toml").write_text(f'''
[test_fragment]
targets = [
    {{ src = "{home}/.config1", actions = {{ after_apply = "exit 1" }} }},
    {{ src = "{home}/.config2", actions = {{ after_apply = "touch success_marker.txt" }} }}
]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--apply"])

    # When
    main()
    terminal.render()

    # Then
    assert (home / ".config1").read_text() == "content1"
    assert (home / ".config2").read_text() == "content2"
    assert (frag / "success_marker.txt").exists()

    terminal.assert_lines(
        [
            "Performing apply for test_fragment fragments.",
            "",
            "Processing fragment test_fragment.",
            f'Copying "./fragments/test_fragment/.config1" to "{home}/.config1" [ DONE].',
            "Running after_apply for test_fragment/.config1 [󰚌 FAIL] (exit code 1).",
            f'Copying "./fragments/test_fragment/.config2" to "{home}/.config2" [ DONE].',
            "Running after_apply for test_fragment/.config2 [ DONE] (exit code 0).",
            "Finished processing fragment test_fragment [ DONE].",
        ]
    )


def test_apply_runs_target_after_apply_for_each_target(tmp_path, monkeypatch, terminal):
    """--apply runs after_apply for each target independently."""

    # Given
    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()

    frag = repo / "fragments" / "test_fragment"
    frag.mkdir(parents=True)
    (frag / ".config_a").write_text("content_a")
    (frag / ".config_b").write_text("content_b")

    (repo / "fragments.toml").write_text(f'''
[test_fragment]
targets = [
    {{ src = "{home}/.config_a", actions = {{ after_apply = "touch marker_a.txt" }} }},
    {{ src = "{home}/.config_b", actions = {{ after_apply = "touch marker_b.txt" }} }}
]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--apply"])

    # When
    main()
    terminal.render()

    # Then
    assert (home / ".config_a").read_text() == "content_a"
    assert (home / ".config_b").read_text() == "content_b"

    assert (frag / "marker_a.txt").exists(), (
        "target after_apply for .config_a did not run"
    )
    assert (frag / "marker_b.txt").exists(), (
        "target after_apply for .config_b did not run"
    )

    terminal.assert_lines(
        [
            "Performing apply for test_fragment fragments.",
            "",
            "Processing fragment test_fragment.",
            f'Copying "./fragments/test_fragment/.config_a" to "{home}/.config_a" [ DONE].',
            "Running after_apply for test_fragment/.config_a [ DONE] (exit code 0).",
            f'Copying "./fragments/test_fragment/.config_b" to "{home}/.config_b" [ DONE].',
            "Running after_apply for test_fragment/.config_b [ DONE] (exit code 0).",
            "Finished processing fragment test_fragment [ DONE].",
        ]
    )


def test_apply_runs_before_apply_target_action_in_fragment_directory(
    tmp_path, monkeypatch, terminal
):
    """--apply runs target's before_apply action before copying the target file."""

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
targets = [{{ src = "{home}/.testrc", actions = {{ before_apply = "pwd > cwd.txt && echo before > order.txt", after_apply = "echo after >> order.txt" }} }}]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--apply"])

    # When
    main()
    terminal.render()

    # Then
    assert (home / ".testrc").read_text() == "applied_content"

    cwd_marker = fragments_dir / "cwd.txt"
    assert cwd_marker.exists(), "target before_apply action did not run"
    assert cwd_marker.read_text().strip() == str(fragments_dir)

    order_marker = fragments_dir / "order.txt"
    assert order_marker.exists()
    assert order_marker.read_text() == "before\nafter\n"

    terminal.assert_lines(
        [
            "Performing apply for test_fragment_1 fragments.",
            "",
            "Processing fragment test_fragment_1.",
            "Running before_apply for test_fragment_1/.testrc [ DONE] (exit code 0).",
            f'Copying "./fragments/test_fragment_1/.testrc" to "{home}/.testrc" [ DONE].',
            "Running after_apply for test_fragment_1/.testrc [ DONE] (exit code 0).",
            "Finished processing fragment test_fragment_1 [ DONE].",
        ]
    )


def test_apply_does_not_run_target_before_apply_when_not_defined_or_empty(
    tmp_path, monkeypatch, terminal
):
    """--apply does not run target's before_apply when not defined or empty."""

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
targets = [{{ src = "{home}/.config2", actions = {{ before_apply = "" }} }}]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--apply"])

    # When
    main()
    terminal.render()

    # Then
    assert (home / ".config1").read_text() == "content1"
    assert (home / ".config2").read_text() == "content2"

    assert not (frag1 / "marker.txt").exists()
    assert not (frag2 / "marker.txt").exists()

    terminal.assert_lines(
        [
            "Performing apply for empty_before_apply_fragment, no_actions_fragment fragments.",
            "",
            "Processing fragment empty_before_apply_fragment.",
            f'Copying "./fragments/empty_before_apply_fragment/.config2" to "{home}/.config2" [ DONE].',
            "Finished processing fragment empty_before_apply_fragment [ DONE].",
            "",
            "Processing fragment no_actions_fragment.",
            f'Copying "./fragments/no_actions_fragment/.config1" to "{home}/.config1" [ DONE].',
            "Finished processing fragment no_actions_fragment [ DONE].",
        ]
    )


def test_apply_skips_target_when_before_apply_fails(tmp_path, monkeypatch, terminal):
    """--apply skips copying and after_apply for target when before_apply fails, continues with other targets."""

    # Given
    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()

    frag = repo / "fragments" / "test_fragment"
    frag.mkdir(parents=True)
    (frag / ".config1").write_text("content1")
    (frag / ".config2").write_text("content2")

    (repo / "fragments.toml").write_text(f'''
[test_fragment]
targets = [
    {{ src = "{home}/.config1", actions = {{ before_apply = "exit 1", after_apply = "touch after_marker1.txt" }} }},
    {{ src = "{home}/.config2", actions = {{ before_apply = "touch before_marker2.txt", after_apply = "touch after_marker2.txt" }} }}
]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--apply"])

    # When
    main()
    terminal.render()

    # Then
    assert not (home / ".config1").exists(), (
        "File should not be copied when target before_apply fails"
    )
    assert not (frag / "after_marker1.txt").exists(), (
        "target after_apply should not run when before_apply fails"
    )

    assert (home / ".config2").read_text() == "content2"
    assert (frag / "before_marker2.txt").exists()
    assert (frag / "after_marker2.txt").exists()

    terminal.assert_lines(
        [
            "Performing apply for test_fragment fragments.",
            "",
            "Processing fragment test_fragment.",
            "Running before_apply for test_fragment/.config1 [󰚌 FAIL] (exit code 1).",
            "Skipping target .config1 because of failed before action [ SKIP].",
            "Running before_apply for test_fragment/.config2 [ DONE] (exit code 0).",
            f'Copying "./fragments/test_fragment/.config2" to "{home}/.config2" [ DONE].',
            "Running after_apply for test_fragment/.config2 [ DONE] (exit code 0).",
            "Finished processing fragment test_fragment [ DONE].",
        ]
    )


def test_apply_runs_target_before_apply_for_each_target(
    tmp_path, monkeypatch, terminal
):
    """--apply runs before_apply for each target independently."""

    # Given
    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()

    frag = repo / "fragments" / "test_fragment"
    frag.mkdir(parents=True)
    (frag / ".config_a").write_text("content_a")
    (frag / ".config_b").write_text("content_b")

    (repo / "fragments.toml").write_text(f'''
[test_fragment]
targets = [
    {{ src = "{home}/.config_a", actions = {{ before_apply = "touch marker_a.txt" }} }},
    {{ src = "{home}/.config_b", actions = {{ before_apply = "touch marker_b.txt" }} }}
]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--apply"])

    # When
    main()
    terminal.render()

    # Then
    assert (home / ".config_a").read_text() == "content_a"
    assert (home / ".config_b").read_text() == "content_b"

    assert (frag / "marker_a.txt").exists(), (
        "target before_apply for .config_a did not run"
    )
    assert (frag / "marker_b.txt").exists(), (
        "target before_apply for .config_b did not run"
    )

    terminal.assert_lines(
        [
            "Performing apply for test_fragment fragments.",
            "",
            "Processing fragment test_fragment.",
            "Running before_apply for test_fragment/.config_a [ DONE] (exit code 0).",
            f'Copying "./fragments/test_fragment/.config_a" to "{home}/.config_a" [ DONE].',
            "Running before_apply for test_fragment/.config_b [ DONE] (exit code 0).",
            f'Copying "./fragments/test_fragment/.config_b" to "{home}/.config_b" [ DONE].',
            "Finished processing fragment test_fragment [ DONE].",
        ]
    )


def test_apply_target_actions_combined_with_fragment_actions(
    tmp_path, monkeypatch, terminal
):
    """--apply runs both fragment and target actions in correct order."""

    # Given
    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()
    fragments_dir = repo / "fragments" / "test_fragment"
    fragments_dir.mkdir(parents=True)
    (fragments_dir / ".testrc").write_text("applied_content")

    (repo / "fragments.toml").write_text(f'''
[test_fragment]
targets = [{{ src = "{home}/.testrc", actions = {{ before_apply = "echo target_before >> order.txt", after_apply = "echo target_after >> order.txt" }} }}]

[test_fragment.actions]
before_apply = "echo fragment_before > order.txt"
after_apply = "echo fragment_after >> order.txt"
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--apply"])

    # When
    main()
    terminal.render()

    # Then
    assert (home / ".testrc").read_text() == "applied_content"

    order_marker = fragments_dir / "order.txt"
    assert order_marker.exists()
    assert (
        order_marker.read_text()
        == "fragment_before\ntarget_before\ntarget_after\nfragment_after\n"
    )

    terminal.assert_lines(
        [
            "Performing apply for test_fragment fragments.",
            "",
            "Processing fragment test_fragment.",
            "Running before_apply for test_fragment [ DONE] (exit code 0).",
            "Running before_apply for test_fragment/.testrc [ DONE] (exit code 0).",
            f'Copying "./fragments/test_fragment/.testrc" to "{home}/.testrc" [ DONE].',
            "Running after_apply for test_fragment/.testrc [ DONE] (exit code 0).",
            "Running after_apply for test_fragment [ DONE] (exit code 0).",
            "Finished processing fragment test_fragment [ DONE].",
        ]
    )
