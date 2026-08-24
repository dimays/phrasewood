"""Integration: evaluate expressions and run effects against a real World,
so effects respect each feature's type and bounds."""

import pytest

from phrasewood import (
    BoolType,
    EnumType,
    Feature,
    FeatureValueError,
    IntType,
    UnknownFeature,
    World,
    WorldEnvironment,
    evaluate,
    execute,
)


def make_env() -> tuple[World, WorldEnvironment]:
    world = World(
        [
            Feature("trust", IntType(0, 5), default=1),
            Feature("has_lantern", BoolType(), default=True),
            Feature("mood", EnumType(("wary", "warm", "cold"))),
        ]
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
