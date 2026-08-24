"""Integration: evaluate expressions and run effects against a real World,
so effects respect each feature's type and bounds."""

import pytest

from phrasewood import (
    BoolType,
    Entity,
    EnumType,
    Feature,
    FeatureValueError,
    IntType,
    UnknownEntity,
    UnknownFeature,
    World,
    WorldEnvironment,
    evaluate,
    execute,
)


def make_env() -> tuple[World, WorldEnvironment]:
    ferryman = Entity(
        "ferryman",
        kind="character",
        features=(
            Feature("mood", EnumType(("wary", "warm", "cold"))),
            Feature("patience", IntType(0, 3), default=1),
        ),
    )
    world = World(
        [
            Feature("trust", IntType(0, 5), default=1),
            Feature("has_lantern", BoolType(), default=True),
            Feature("mood", EnumType(("wary", "warm", "cold"))),
        ],
        entities=[ferryman],
    )
    return world, WorldEnvironment(world)


class TestEvaluateAgainstWorld:
    def test_requirement_reads_live_values(self) -> None:
        world, env = make_env()
        assert evaluate("trust >= 1 and has_lantern", env) is True
        world.set("has_lantern", False)
        assert evaluate("trust >= 1 and has_lantern", env) is False

    def test_enum_equality(self) -> None:
        _, env = make_env()
        assert evaluate("mood == 'wary'", env) is True

    def test_unknown_feature_raises(self) -> None:
        _, env = make_env()
        with pytest.raises(UnknownFeature):
            evaluate("missing", env)


class TestEffectsAgainstWorld:
    def test_effect_mutates_the_world(self) -> None:
        world, env = make_env()
        execute("trust += 2; mood = 'warm'", env)
        assert world.get("trust") == 3
        assert world.get("mood") == "warm"

    def test_effect_respects_feature_bounds(self) -> None:
        world, env = make_env()
        execute("trust += 100", env)
        assert world.get("trust") == 5  # clamped by the feature, not the language

    def test_effect_rejects_invalid_enum_value(self) -> None:
        _, env = make_env()
        with pytest.raises(FeatureValueError):
            execute("mood = 'furious'", env)


class TestEntityAttributes:
    def test_reads_an_entity_feature(self) -> None:
        _, env = make_env()
        # world "mood" and the ferryman's "mood" are separate namespaces.
        assert evaluate("ferryman.mood == 'wary'", env) is True

    def test_effect_writes_an_entity_feature(self) -> None:
        world, env = make_env()
        execute("ferryman.mood = 'warm'", env)
        assert world.get_entity_feature("ferryman", "mood") == "warm"

    def test_entity_effect_respects_bounds(self) -> None:
        world, env = make_env()
        execute("ferryman.patience += 5", env)
        assert world.get_entity_feature("ferryman", "patience") == 3  # clamped

    def test_entity_effect_rejects_invalid_value(self) -> None:
        _, env = make_env()
        with pytest.raises(FeatureValueError):
            execute("ferryman.mood = 'furious'", env)

    def test_unknown_entity_raises(self) -> None:
        _, env = make_env()
        with pytest.raises(UnknownEntity):
            evaluate("nobody.mood == 'wary'", env)
