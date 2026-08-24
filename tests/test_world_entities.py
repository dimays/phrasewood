"""Tests for entity state held by the World."""

import pytest

from phrasewood import (
    DuplicateEntity,
    Entity,
    EnumType,
    Feature,
    IntType,
    UnknownEntity,
    UnknownFeature,
    World,
)


def make_world() -> World:
    ferryman = Entity(
        "ferryman",
        kind="character",
        features=(
            Feature("mood", EnumType(("wary", "warm", "cold"))),
            Feature("patience", IntType(0, 3), default=1),
        ),
    )
    return World([Feature("chapter", IntType(), default=1)], entities=[ferryman])


class TestEntityRegistry:
    def test_lookup_and_listing(self) -> None:
        world = make_world()
        assert world.has_entity("ferryman")
        assert not world.has_entity("nobody")
        assert world.entity("ferryman").kind == "character"
        assert tuple(e.id for e in world.entities()) == ("ferryman",)

    def test_unknown_entity_raises(self) -> None:
        with pytest.raises(UnknownEntity):
            make_world().entity("nobody")

    def test_duplicate_entity_is_rejected(self) -> None:
        with pytest.raises(DuplicateEntity):
            World([], entities=[Entity("ferryman"), Entity("ferryman")])


class TestEntityFeatures:
    def test_defaults(self) -> None:
        world = make_world()
        assert world.get_entity_feature("ferryman", "mood") == "wary"
        assert world.get_entity_feature("ferryman", "patience") == 1

    def test_set_is_validated_and_clamped(self) -> None:
        world = make_world()
        assert world.set_entity_feature("ferryman", "patience", 99) == 3
        world.set_entity_feature("ferryman", "mood", "warm")
        assert world.get_entity_feature("ferryman", "mood") == "warm"

    def test_unknown_entity_feature_raises(self) -> None:
        with pytest.raises(UnknownFeature):
            make_world().get_entity_feature("ferryman", "nonexistent")

    def test_feature_access_on_unknown_entity_raises(self) -> None:
        with pytest.raises(UnknownEntity):
            make_world().get_entity_feature("nobody", "mood")

    def test_snapshot(self) -> None:
        world = make_world()
        assert world.entity_snapshot("ferryman") == {"mood": "wary", "patience": 1}


class TestEntitiesAreSeparateFromWorldFeatures:
    def test_world_features_untouched_by_entities(self) -> None:
        world = make_world()
        assert world.get("chapter") == 1
        assert "ferryman" not in world  # membership sugar is world features only
        assert set(world) == {"chapter"}
