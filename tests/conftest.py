import pyte
import pytest


@pytest.fixture
def terminal(capsys):
    class VirtualTerminal:
        def __init__(self):
            self.screen = pyte.Screen(800, 24)
            self.stream = pyte.Stream(self.screen)

        def render(self):
            self.stream.feed(capsys.readouterr().out)

        @property
        def lines(self):
            return [
                line.strip()
                for line in "\n".join(self.screen.display).strip().split("\n")
            ]

        def assert_lines(self, lines: list[str]):
            assert len(lines) == len(self.lines)
            for expect, actual in zip(lines, self.lines):
                assert actual in expect

        def debug_print_lines(self):
            print("=== DEBUG TERMINAL LINES ===")
            for line in self.lines:
                print(line)
            print("=== END DEBUG TERMINAL LINES ===")

    return VirtualTerminal()
