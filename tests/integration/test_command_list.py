import sys

from src.nastrajacz import main


def test_list_shows_all_fragments(tmp_path, monkeypatch, terminal):
    """--list displays all fragment names from config."""

    # Given
    (tmp_path / "fragments.toml").write_text("""
[test_fragment_1]
targets = []

[test_fragment_2]
targets = []

[test_fragment_3]
targets = []
""")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["nastrajacz", "--list"])

    # When
    main()
    terminal.render()

    # Then
    terminal.assert_lines(
        [
            "Fragments defined in configuration file:",
            "test_fragment_1, test_fragment_2, test_fragment_3",
        ]
    )
