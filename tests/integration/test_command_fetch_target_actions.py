import sys

from src.nastrajacz import main


def test_fetch_runs_after_fetch_target_action_in_fragments_parent_directory(
    tmp_path, monkeypatch, terminal
):
    """--fetch runs target's after_fetch action after copying the target file, in the fragments parent directory."""

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
targets = [{{ src = "{home}/.testrc", actions = {{ after_fetch = "pwd > cwd.txt" }} }}]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--fetch"])

    # When
    main()
    terminal.render()

    # Then
    assert (fragments_dir / ".testrc").read_text() == "fetched_content"

    # Target actions run in the parent of fragment directory (./fragments/)
    fragments_parent = repo / "fragments"
    cwd_marker = fragments_parent / "cwd.txt"
    assert cwd_marker.exists(), "target after_fetch action did not run"
    assert cwd_marker.read_text().strip() == str(fragments_parent)

    terminal.assert_lines(
        [
            "Performing fetch for test_fragment_1 fragments.",
            "",
            "Processing fragment test_fragment_1.",
            f'Copying "{home}/.testrc" to "./fragments/test_fragment_1" [ DONE].',
            "Running after_fetch for test_fragment_1/.testrc [ DONE] (exit code 0).",
            "Finished processing fragment test_fragment_1 [ DONE].",
        ]
    )


def test_fetch_does_not_run_target_after_fetch_when_not_defined_or_empty(
    tmp_path, monkeypatch, terminal
):
    """--fetch does not run target's after_fetch when not defined or empty."""

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
targets = [{{ src = "{home}/.config2", actions = {{ after_fetch = "" }} }}]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--fetch"])

    # When
    main()
    terminal.render()

    # Then
    frag1 = repo / "fragments" / "no_actions_fragment"
    frag2 = repo / "fragments" / "empty_after_fetch_fragment"
    fragments_parent = repo / "fragments"

    assert (frag1 / ".config1").read_text() == "content1"
    assert (frag2 / ".config2").read_text() == "content2"

    assert not (fragments_parent / "cwd.txt").exists()

    terminal.assert_lines(
        [
            "Performing fetch for empty_after_fetch_fragment, no_actions_fragment fragments.",
            "",
            "Processing fragment empty_after_fetch_fragment.",
            f'Copying "{home}/.config2" to "./fragments/empty_after_fetch_fragment" [ DONE].',
            "Finished processing fragment empty_after_fetch_fragment [ DONE].",
            "",
            "Processing fragment no_actions_fragment.",
            f'Copying "{home}/.config1" to "./fragments/no_actions_fragment" [ DONE].',
            "Finished processing fragment no_actions_fragment [ DONE].",
        ]
    )


def test_fetch_prints_warning_when_target_after_fetch_fails(
    tmp_path, monkeypatch, terminal
):
    """--fetch prints warning when target's after_fetch fails but continues with other targets."""

    # Given
    home = tmp_path / "home"
    home.mkdir()
    (home / ".config1").write_text("content1")
    (home / ".config2").write_text("content2")

    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "fragments.toml").write_text(f'''
[test_fragment]
targets = [
    {{ src = "{home}/.config1", actions = {{ after_fetch = "exit 1" }} }},
    {{ src = "{home}/.config2", actions = {{ after_fetch = "touch success_marker.txt" }} }}
]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--fetch"])

    # When
    main()
    terminal.render()

    # Then
    frag = repo / "fragments" / "test_fragment"
    fragments_parent = repo / "fragments"

    assert (frag / ".config1").read_text() == "content1"
    assert (frag / ".config2").read_text() == "content2"

    # Marker created in fragments parent directory
    assert (fragments_parent / "success_marker.txt").exists()

    terminal.assert_lines(
        [
            "Performing fetch for test_fragment fragments.",
            "",
            "Processing fragment test_fragment.",
            f'Copying "{home}/.config1" to "./fragments/test_fragment" [ DONE].',
            "Running after_fetch for test_fragment/.config1 [󰚌 FAIL] (exit code 1).",
            f'Copying "{home}/.config2" to "./fragments/test_fragment" [ DONE].',
            "Running after_fetch for test_fragment/.config2 [ DONE] (exit code 0).",
            "Finished processing fragment test_fragment [ DONE].",
        ]
    )


def test_fetch_runs_target_after_fetch_for_each_target(tmp_path, monkeypatch, terminal):
    """--fetch runs after_fetch for each target independently."""

    # Given
    home = tmp_path / "home"
    home.mkdir()
    (home / ".config_a").write_text("content_a")
    (home / ".config_b").write_text("content_b")

    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "fragments.toml").write_text(f'''
[test_fragment]
targets = [
    {{ src = "{home}/.config_a", actions = {{ after_fetch = "touch marker_a.txt" }} }},
    {{ src = "{home}/.config_b", actions = {{ after_fetch = "touch marker_b.txt" }} }}
]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--fetch"])

    # When
    main()
    terminal.render()

    # Then
    frag = repo / "fragments" / "test_fragment"
    fragments_parent = repo / "fragments"

    assert (frag / ".config_a").read_text() == "content_a"
    assert (frag / ".config_b").read_text() == "content_b"

    # Markers created in fragments parent directory
    assert (fragments_parent / "marker_a.txt").exists(), (
        "target after_fetch for .config_a did not run"
    )
    assert (fragments_parent / "marker_b.txt").exists(), (
        "target after_fetch for .config_b did not run"
    )

    terminal.assert_lines(
        [
            "Performing fetch for test_fragment fragments.",
            "",
            "Processing fragment test_fragment.",
            f'Copying "{home}/.config_a" to "./fragments/test_fragment" [ DONE].',
            "Running after_fetch for test_fragment/.config_a [ DONE] (exit code 0).",
            f'Copying "{home}/.config_b" to "./fragments/test_fragment" [ DONE].',
            "Running after_fetch for test_fragment/.config_b [ DONE] (exit code 0).",
            "Finished processing fragment test_fragment [ DONE].",
        ]
    )


def test_fetch_runs_before_fetch_target_action_in_fragments_parent_directory(
    tmp_path, monkeypatch, terminal
):
    """--fetch runs target's before_fetch action before copying the target file, in the fragments parent directory."""

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
targets = [{{ src = "{home}/.testrc", actions = {{ before_fetch = "pwd > cwd.txt && echo before > order.txt", after_fetch = "echo after >> order.txt" }} }}]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--fetch"])

    # When
    main()
    terminal.render()

    # Then
    assert (fragments_dir / ".testrc").read_text() == "fetched_content"

    # Target actions run in the parent of fragment directory (./fragments/)
    fragments_parent = repo / "fragments"
    cwd_marker = fragments_parent / "cwd.txt"
    assert cwd_marker.exists(), "target before_fetch action did not run"
    assert cwd_marker.read_text().strip() == str(fragments_parent)

    order_marker = fragments_parent / "order.txt"
    assert order_marker.exists()
    assert order_marker.read_text() == "before\nafter\n"

    terminal.assert_lines(
        [
            "Performing fetch for test_fragment_1 fragments.",
            "",
            "Processing fragment test_fragment_1.",
            "Running before_fetch for test_fragment_1/.testrc [ DONE] (exit code 0).",
            f'Copying "{home}/.testrc" to "./fragments/test_fragment_1" [ DONE].',
            "Running after_fetch for test_fragment_1/.testrc [ DONE] (exit code 0).",
            "Finished processing fragment test_fragment_1 [ DONE].",
        ]
    )


def test_fetch_does_not_run_target_before_fetch_when_not_defined_or_empty(
    tmp_path, monkeypatch, terminal
):
    """--fetch does not run target's before_fetch when not defined or empty."""

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
targets = [{{ src = "{home}/.config2", actions = {{ before_fetch = "" }} }}]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--fetch"])

    # When
    main()
    terminal.render()

    # Then
    frag1 = repo / "fragments" / "no_actions_fragment"
    frag2 = repo / "fragments" / "empty_before_fetch_fragment"
    fragments_parent = repo / "fragments"

    assert (frag1 / ".config1").read_text() == "content1"
    assert (frag2 / ".config2").read_text() == "content2"

    assert not (fragments_parent / "marker.txt").exists()

    terminal.assert_lines(
        [
            "Performing fetch for empty_before_fetch_fragment, no_actions_fragment fragments.",
            "",
            "Processing fragment empty_before_fetch_fragment.",
            f'Copying "{home}/.config2" to "./fragments/empty_before_fetch_fragment" [ DONE].',
            "Finished processing fragment empty_before_fetch_fragment [ DONE].",
            "",
            "Processing fragment no_actions_fragment.",
            f'Copying "{home}/.config1" to "./fragments/no_actions_fragment" [ DONE].',
            "Finished processing fragment no_actions_fragment [ DONE].",
        ]
    )


def test_fetch_skips_target_when_before_fetch_fails(tmp_path, monkeypatch, terminal):
    """--fetch skips copying and after_fetch for target when before_fetch fails, continues with other targets."""

    # Given
    home = tmp_path / "home"
    home.mkdir()
    (home / ".config1").write_text("content1")
    (home / ".config2").write_text("content2")

    repo = tmp_path / "repo"
    repo.mkdir()

    # Pre-create fragment directory so before_fetch can run
    frag = repo / "fragments" / "test_fragment"
    frag.mkdir(parents=True)

    (repo / "fragments.toml").write_text(f'''
[test_fragment]
targets = [
    {{ src = "{home}/.config1", actions = {{ before_fetch = "exit 1", after_fetch = "touch after_marker1.txt" }} }},
    {{ src = "{home}/.config2", actions = {{ before_fetch = "touch before_marker2.txt", after_fetch = "touch after_marker2.txt" }} }}
]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--fetch"])

    # When
    main()
    terminal.render()

    # Then
    fragments_parent = repo / "fragments"

    assert not (frag / ".config1").exists(), (
        "File should not be copied when target before_fetch fails"
    )
    assert not (fragments_parent / "after_marker1.txt").exists(), (
        "target after_fetch should not run when before_fetch fails"
    )

    assert (frag / ".config2").read_text() == "content2"
    # Markers created in fragments parent directory
    assert (fragments_parent / "before_marker2.txt").exists()
    assert (fragments_parent / "after_marker2.txt").exists()

    terminal.assert_lines(
        [
            "Performing fetch for test_fragment fragments.",
            "",
            "Processing fragment test_fragment.",
            "Running before_fetch for test_fragment/.config1 [󰚌 FAIL] (exit code 1).",
            "Skipping target .config1 because of failed before action [ SKIP].",
            "Running before_fetch for test_fragment/.config2 [ DONE] (exit code 0).",
            f'Copying "{home}/.config2" to "./fragments/test_fragment" [ DONE].',
            "Running after_fetch for test_fragment/.config2 [ DONE] (exit code 0).",
            "Finished processing fragment test_fragment [ DONE].",
        ]
    )


def test_fetch_runs_target_before_fetch_for_each_target(
    tmp_path, monkeypatch, terminal
):
    """--fetch runs before_fetch for each target independently."""

    # Given
    home = tmp_path / "home"
    home.mkdir()
    (home / ".config_a").write_text("content_a")
    (home / ".config_b").write_text("content_b")

    repo = tmp_path / "repo"
    repo.mkdir()

    frag = repo / "fragments" / "test_fragment"
    frag.mkdir(parents=True)

    (repo / "fragments.toml").write_text(f'''
[test_fragment]
targets = [
    {{ src = "{home}/.config_a", actions = {{ before_fetch = "touch marker_a.txt" }} }},
    {{ src = "{home}/.config_b", actions = {{ before_fetch = "touch marker_b.txt" }} }}
]
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--fetch"])

    # When
    main()
    terminal.render()

    # Then
    fragments_parent = repo / "fragments"

    assert (frag / ".config_a").read_text() == "content_a"
    assert (frag / ".config_b").read_text() == "content_b"

    # Markers created in fragments parent directory
    assert (fragments_parent / "marker_a.txt").exists(), (
        "target before_fetch for .config_a did not run"
    )
    assert (fragments_parent / "marker_b.txt").exists(), (
        "target before_fetch for .config_b did not run"
    )

    terminal.assert_lines(
        [
            "Performing fetch for test_fragment fragments.",
            "",
            "Processing fragment test_fragment.",
            "Running before_fetch for test_fragment/.config_a [ DONE] (exit code 0).",
            f'Copying "{home}/.config_a" to "./fragments/test_fragment" [ DONE].',
            "Running before_fetch for test_fragment/.config_b [ DONE] (exit code 0).",
            f'Copying "{home}/.config_b" to "./fragments/test_fragment" [ DONE].',
            "Finished processing fragment test_fragment [ DONE].",
        ]
    )


def test_fetch_target_actions_combined_with_fragment_actions(
    tmp_path, monkeypatch, terminal
):
    """--fetch runs both fragment and target actions in correct order."""

    # Given
    home = tmp_path / "home"
    home.mkdir()
    (home / ".testrc").write_text("fetched_content")

    repo = tmp_path / "repo"
    repo.mkdir()
    fragments_dir = repo / "fragments" / "test_fragment"
    fragments_dir.mkdir(parents=True)

    # Note: Fragment actions run in fragment directory, target actions run in fragments parent
    # To test order properly, we use the fragment directory for all actions
    (repo / "fragments.toml").write_text(f'''
[test_fragment]
targets = [{{ src = "{home}/.testrc", actions = {{ before_fetch = "echo target_before >> order.txt", after_fetch = "echo target_after >> order.txt" }} }}]

[test_fragment.actions]
before_fetch = "echo fragment_before > order.txt"
after_fetch = "echo fragment_after >> order.txt"
''')

    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--fetch"])

    # When
    main()
    terminal.render()

    # Then
    assert (fragments_dir / ".testrc").read_text() == "fetched_content"

    # Fragment actions run in fragment directory, target actions run in fragments parent
    # The order.txt will be in fragment directory (from fragment before_fetch)
    # Target actions will create/append to order.txt in fragments parent directory
    fragment_order = fragments_dir / "order.txt"
    assert fragment_order.exists()
    # Only fragment actions write to fragment directory
    assert fragment_order.read_text() == "fragment_before\nfragment_after\n"

    # Target actions write to fragments parent directory
    fragments_parent = repo / "fragments"
    target_order = fragments_parent / "order.txt"
    assert target_order.exists()
    assert target_order.read_text() == "target_before\ntarget_after\n"

    terminal.assert_lines(
        [
            "Performing fetch for test_fragment fragments.",
            "",
            "Processing fragment test_fragment.",
            "Running before_fetch for test_fragment [ DONE] (exit code 0).",
            "Running before_fetch for test_fragment/.testrc [ DONE] (exit code 0).",
            f'Copying "{home}/.testrc" to "./fragments/test_fragment" [ DONE].',
            "Running after_fetch for test_fragment/.testrc [ DONE] (exit code 0).",
            "Running after_fetch for test_fragment [ DONE] (exit code 0).",
            "Finished processing fragment test_fragment [ DONE].",
        ]
    )
