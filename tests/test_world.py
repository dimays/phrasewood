"""Tests for the World — the mutable state of a playthrough."""

import pytest

from phrasewood import (
    BoolType,
    DuplicateFeature,
    EnumType,
    Feature,
    FeatureValueError,
    IntType,
    UnknownFeature,
    World,
)


def make_world() -> World:
    return World(
        [
            Feature("trust", IntType(0, 5), default=1),
            Feature("has_lantern", BoolType(), default=True),
            Feature("mood", EnumType(("wary", "warm", "cold"))),
        ]
    )


class TestConstruction:
    def test_starts_each_feature_at_its_default(self) -> None:
        w = make_world()
        assert w.get("trust") == 1
        assert w.get("has_lantern") is True
        assert w.get("mood") == "wary"  # enum's first value

    def test_applies_opening_values(self) -> None:
        w = World([Feature("trust", IntType(0, 5))], values={"trust": 3})
        assert w.get("trust") == 3

    def test_opening_values_are_clamped(self) -> None:
        w = World([Feature("trust", IntType(0, 5))], values={"trust": 99})
        assert w.get("trust") == 5

    def test_rejects_duplicate_feature_names(self) -> None:
        with pytest.raises(DuplicateFeature):
            World([Feature("trust", IntType()), Feature("trust", BoolType())])


class TestReadsAndWrites:
    def test_set_then_get(self) -> None:
        w = make_world()
        w.set("trust", 4)
        assert w.get("trust") == 4

    def test_set_clamps_to_bounds(self) -> None:
        w = make_world()
        assert w.set("trust", 100) == 5
        assert w.get("trust") == 5

    def test_set_validates_type(self) -> None:
        w = make_world()
        with pytest.raises(FeatureValueError):
            w.set("has_lantern", "yes")

    def test_get_unknown_feature_raises(self) -> None:
        with pytest.raises(UnknownFeature):
            make_world().get("nonexistent")

    def test_set_unknown_feature_raises(self) -> None:
        with pytest.raises(UnknownFeature):
            make_world().set("nonexistent", 1)

    def test_has(self) -> None:
        w = make_world()
        assert w.has("trust")
        assert not w.has("nonexistent")


class TestResetAndSnapshot:
    def test_reset_one_feature(self) -> None:
        w = make_world()
        w.set("trust", 4)
        w.reset("trust")
        assert w.get("trust") == 1

    def test_reset_all_features(self) -> None:
        w = make_world()
        w.set("trust", 4)
        w.set("has_lantern", False)
        w.reset()
        assert w.get("trust") == 1
        assert w.get("has_lantern") is True

    def test_snapshot_is_a_detached_copy(self) -> None:
        w = make_world()
        snap = w.snapshot()
        snap["trust"] = 999
        assert w.get("trust") == 1  # mutating the snapshot doesn't touch the world


class TestMappingSugar:
    def test_getitem_and_setitem(self) -> None:
        w = make_world()
        w["trust"] = 2
        assert w["trust"] == 2

    def test_contains(self) -> None:
        w = make_world()
        assert "trust" in w
        assert "nope" not in w

    def test_len_and_iter(self) -> None:
        w = make_world()
        assert len(w) == 3
        assert set(w) == {"trust", "has_lantern", "mood"}
