"""Tests for the .pwood serializer — round-trip fidelity and terse output."""

from collections.abc import Callable
from pathlib import Path

from phrasewood import (
    Bud,
    Choice,
    Entity,
    EnumType,
    Feature,
    IntType,
    Tree,
    load,
    play,
    save,
)

REFERENCE = Path(__file__).resolve().parent.parent / "examples" / "the-lamplighters-debt"


def scripted(lines: list[str]) -> Callable[[], str | None]:
    it = iter(lines)
    return lambda: next(it, None)


class TestRoundTrip:
    def test_folder_round_trip_is_faithful(self, tmp_path: Path) -> None:
        original = load(REFERENCE)
        save(original, tmp_path / "out")
        assert load(tmp_path / "out") == original

    def test_pwood_zip_round_trip_is_faithful(self, tmp_path: Path) -> None:
        original = load(REFERENCE)
        archive = tmp_path / "game.pwood"
        save(original, archive)
        assert archive.is_file()
        assert load(archive) == original

    def test_a_hand_built_tree_round_trips(self, tmp_path: Path) -> None:
        original = Tree(
            "demo",
            title="Demo",
            features=(Feature("trust", IntType(0, 5), default=1, help="how trusted"),),
            entities=(
                Entity(
                    "ferryman", kind="character", features=(Feature("mood", EnumType(("a", "b"))),)
                ),
            ),
            buds=(
                Bud("start", content="Hello.", once=True, choices=(Choice("go", do="trust += 1"),)),
            ),
            start="start",
        )
        save(original, tmp_path / "out")
        assert load(tmp_path / "out") == original

    def test_reloaded_game_plays_the_same(self, tmp_path: Path) -> None:
        save(load(REFERENCE), tmp_path / "out")
        out: list[str] = []
        session = play(load(tmp_path / "out"), read=scripted(["1", "1", "1"]), write=out.append)
        assert session.is_over()
        assert "unquenched" in "\n".join(out)


class TestTerseOutput:
    def test_defaults_and_empties_are_omitted(self, tmp_path: Path) -> None:
        save(load(REFERENCE), tmp_path / "out")
        bridge = (tmp_path / "out" / "buds" / "bridge.md").read_text()
        assert "title:" not in bridge  # the bud has no title
        lantern = (tmp_path / "out" / "entities" / "lantern.yaml").read_text()
        assert "kind:" not in lantern  # 'thing' is the default kind
