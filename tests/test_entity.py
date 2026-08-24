"""Tests for the Entity definition."""

import pytest

from phrasewood import DuplicateFeature, Entity, EnumType, Feature, IntType, PhrasewoodError


class TestEntity:
    def test_basic_definition(self) -> None:
        ferryman = Entity(
            "ferryman",
            kind="character",
            name="the ferryman",
            features=(Feature("mood", EnumType(("wary", "warm", "cold"))),),
            aliases=("boatman", "him"),
            description="A hooded figure at the oars.",
        )
        assert ferryman.id == "ferryman"
        assert ferryman.kind == "character"
        assert ferryman.name == "the ferryman"
        assert ferryman.feature_names() == ("mood",)

    def test_id_is_required(self) -> None:
        with pytest.raises(PhrasewoodError):
            Entity("")

    def test_name_falls_back_to_id(self) -> None:
        assert Entity("the-bridge").name == "the-bridge"

    def test_features_and_aliases_normalize_to_tuples(self) -> None:
        entity = Entity(
            "chest",
            features=[Feature("locked", IntType(0, 1))],
            aliases=["box", "coffer"],
        )
        assert isinstance(entity.features, tuple)
        assert isinstance(entity.aliases, tuple)

    def test_duplicate_feature_is_rejected(self) -> None:
        with pytest.raises(DuplicateFeature):
            Entity("x", features=(Feature("a", IntType()), Feature("a", IntType())))

    def test_is_immutable(self) -> None:
        from dataclasses import FrozenInstanceError

        entity = Entity("ferryman")
        with pytest.raises(FrozenInstanceError):
            entity.kind = "place"  # type: ignore[misc]
