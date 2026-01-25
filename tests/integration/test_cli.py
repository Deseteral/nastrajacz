import sys

from src.nastrajacz import main


def test_error_no_fragments_file(tmp_path, monkeypatch, terminal):
    """Shows error when fragments.toml does not exist."""

    # Given
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--list"])

    # When
    main()
    terminal.render()

    # Then
    terminal.assert_lines(
        [
            "There is no fragments file at this location.",
        ]
    )


def test_error_invalid_toml(tmp_path, monkeypatch, terminal):
    """Shows error when fragments.toml is invalid."""

    # Given
    (tmp_path / "fragments.toml").write_text("this is not valid toml")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--list"])

    # When
    main()
    terminal.render()

    # Then
    terminal.assert_lines(
        [
            "Could not read fragments config file.",
        ]
    )


def test_error_nonexistent_fragment_selected(tmp_path, monkeypatch, terminal):
    """Shows error when selected fragment does not exist in config."""

    # Given
    (tmp_path / "fragments.toml").write_text("""
[test_fragment_1]
targets = []
""")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys, "argv", ["nastrajacz", "--fetch", "--select", "nonexistent"]
    )

    # When
    main()
    terminal.render()

    # Then
    terminal.assert_lines(
        [
            "Cannot perform operations without selected fragments.",
        ]
    )
