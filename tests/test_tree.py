"""Tests for the Tree — its integrity checks and its bridge to a World."""

import pytest

from phrasewood import (
    Bud,
    Choice,
    DuplicateBud,
    DuplicateFeature,
    Entity,
    EnumType,
    Feature,
    IntType,
    PhrasewoodError,
    Tree,
    UnknownBud,
    World,
    WorldEnvironment,
    eval_expression,
    run_effect,
)


def make_tree() -> Tree:
    return Tree(
        id="the-lamplighters-debt",
        title="The Lamplighter's Debt",
        author="David Mays",
        version="0.1.0",
        created="2026-08-23",
        features=(Feature("trust", IntType(0, 5), default=1),),
        entities=(Entity("ferryman", features=(Feature("mood", EnumType(("wary", "warm"))),)),),
        buds=(
            Bud(
                "start",
                content="The bridge is out.",
                when="trust >= 1",
                choices=(
                    Choice("warm up", do="trust += 1; ferryman.mood = 'warm'", goto="crossing"),
                ),
            ),
            Bud("crossing", content="You cross."),
        ),
        start="start",
    )


class TestConstruction:
    def test_metadata_and_collections(self) -> None:
        tree = make_tree()
        assert tree.title == "The Lamplighter's Debt"
        assert tree.author == "David Mays"
        assert isinstance(tree.buds, tuple)
        assert tree.has_bud("start")
        assert tree.bud("crossing").content == "You cross."

    def test_requires_an_id(self) -> None:
        with pytest.raises(PhrasewoodError):
            Tree("")

    def test_unknown_bud_lookup_raises(self) -> None:
        with pytest.raises(UnknownBud):
            make_tree().bud("nowhere")


class TestIntegrity:
    def test_rejects_duplicate_features(self) -> None:
        with pytest.raises(DuplicateFeature):
            Tree("t", features=(Feature("a", IntType()), Feature("a", IntType())))

    def test_rejects_duplicate_buds(self) -> None:
        with pytest.raises(DuplicateBud):
            Tree("t", buds=(Bud("x"), Bud("x")))

    def test_rejects_unknown_start(self) -> None:
        with pytest.raises(UnknownBud):
            Tree("t", buds=(Bud("only"),), start="missing")

    def test_rejects_dangling_goto(self) -> None:
        with pytest.raises(UnknownBud):
            Tree("t", buds=(Bud("only", choices=(Choice("go", goto="nowhere"),)),))

    def test_accepts_valid_references(self) -> None:
        # make_tree() has a valid start and a valid goto; constructing it is the test.
        assert make_tree().start == "start"


class TestWorldBridge:
    def test_for_tree_builds_features_and_entities(self) -> None:
        world = World.for_tree(make_tree())
        assert world.get("trust") == 1
        assert world.get_entity_feature("ferryman", "mood") == "wary"

    def test_compiled_condition_and_effect_run_against_the_world(self) -> None:
        tree = make_tree()
        world = World.for_tree(tree)
        env = WorldEnvironment(world)

        start = tree.bud("start")
        assert eval_expression(start.condition, env) is True

        run_effect(start.choices[0].effect, env)
        assert world.get("trust") == 2
        assert world.get_entity_feature("ferryman", "mood") == "warm"
