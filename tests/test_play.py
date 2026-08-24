"""Tests for the terminal player, driven with scripted input/output."""

from collections.abc import Callable

from phrasewood import Bud, Choice, Tree, play
from phrasewood.examples import lamplighter


def scripted(lines: list[str]) -> Callable[[], str | None]:
    """A reader that yields each line in turn, then None (as EOF/quit)."""
    it = iter(lines)
    return lambda: next(it, None)


def small_tree() -> Tree:
    return Tree(
        "t",
        buds=(
            Bud("start", content="Start.", once=True, choices=(Choice("go", goto="fin"),)),
            Bud("fin", content="Fin.", once=True),
        ),
        start="start",
    )


class TestLoop:
    def test_renders_and_plays_to_the_end(self) -> None:
        out: list[str] = []
        play(small_tree(), read=scripted(["1"]), write=out.append)
        text = "\n".join(out)
        assert "Start." in text
        assert "1. go" in text
        assert "Fin." in text
        assert "the end" in text.lower()

    def test_invalid_input_reprompts(self) -> None:
        out: list[str] = []
        play(small_tree(), read=scripted(["banana", "1"]), write=out.append)
        assert any("Please choose" in line for line in out)

    def test_quit_leaves_early(self) -> None:
        out: list[str] = []
        session = play(small_tree(), read=scripted(["q"]), write=out.append)
        assert not session.is_over()
        assert any("wood" in line for line in out)

    def test_eof_leaves_gracefully(self) -> None:
        out: list[str] = []
        play(small_tree(), read=scripted([]), write=out.append)  # None on first read
        assert any("wood" in line for line in out)


class TestBundledGame:
    def test_warm_ending(self) -> None:
        out: list[str] = []
        session = play(lamplighter(), read=scripted(["1", "1", "1"]), write=out.append)
        assert session.is_over()
        assert "unquenched" in "\n".join(out)  # the warm ending's prose

    def test_cold_ending(self) -> None:
        out: list[str] = []
        session = play(lamplighter(), read=scripted(["2", "1"]), write=out.append)
        assert session.is_over()
        assert "never knew" in "\n".join(out)  # the cold ending's prose
