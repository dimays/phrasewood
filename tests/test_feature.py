"""Tests for feature types and the Feature binding."""

from dataclasses import FrozenInstanceError

import pytest

from phrasewood import (
    BoolType,
    EnumType,
    Feature,
    FeatureValueError,
    IntType,
    TextType,
)


class TestIntType:
    def test_accepts_integers(self) -> None:
        assert IntType().coerce(7) == 7

    def test_rejects_non_integers(self) -> None:
        with pytest.raises(FeatureValueError):
            IntType().coerce("3")

    def test_rejects_booleans(self) -> None:
        # True == 1 in Python; a numeric feature must not accept it silently.
        with pytest.raises(FeatureValueError):
            IntType().coerce(True)

    def test_clamps_to_bounds(self) -> None:
        t = IntType(min=0, max=5)
        assert t.clamp(-3) == 0
        assert t.clamp(9) == 5
        assert t.clamp(4) == 4

    def test_rejects_inverted_bounds(self) -> None:
        with pytest.raises(FeatureValueError):
            IntType(min=5, max=0)

    def test_natural_default_respects_min(self) -> None:
        assert IntType().natural_default() == 0
        assert IntType(min=3).natural_default() == 3


class TestBoolType:
    def test_accepts_booleans(self) -> None:
        assert BoolType().coerce(True) is True

    def test_rejects_non_booleans(self) -> None:
        with pytest.raises(FeatureValueError):
            BoolType().coerce(1)

    def test_natural_default_is_false(self) -> None:
        assert BoolType().natural_default() is False


class TestTextType:
    def test_accepts_text(self) -> None:
        assert TextType().coerce("hello") == "hello"

    def test_rejects_non_text(self) -> None:
        with pytest.raises(FeatureValueError):
            TextType().coerce(42)

    def test_natural_default_is_empty(self) -> None:
        assert TextType().natural_default() == ""


class TestEnumType:
    def test_accepts_declared_values(self) -> None:
        t = EnumType(("wary", "warm", "cold"))
        assert t.coerce("warm") == "warm"

    def test_rejects_undeclared_values(self) -> None:
        t = EnumType(("wary", "warm"))
        with pytest.raises(FeatureValueError):
            t.coerce("furious")

    def test_requires_at_least_one_value(self) -> None:
        with pytest.raises(FeatureValueError):
            EnumType(())

    def test_rejects_duplicate_values(self) -> None:
        with pytest.raises(FeatureValueError):
            EnumType(("warm", "warm"))

    def test_normalizes_sequence_to_tuple(self) -> None:
        t = EnumType(["a", "b"])  # a list is fine on the way in
        assert t.values == ("a", "b")

    def test_natural_default_is_first_value(self) -> None:
        assert EnumType(("a", "b")).natural_default() == "a"


class TestFeature:
    def test_uses_type_natural_default_when_unset(self) -> None:
        assert Feature("chapter", IntType()).default == 0
        assert Feature("lit", BoolType()).default is False

    def test_validates_and_clamps_explicit_default(self) -> None:
        assert Feature("trust", IntType(0, 5), default=99).default == 5

    def test_rejects_impossible_default_at_definition_time(self) -> None:
        with pytest.raises(FeatureValueError):
            Feature("mood", EnumType(("wary", "warm")), default="furious")

    def test_requires_a_name(self) -> None:
        with pytest.raises(FeatureValueError):
            Feature("", IntType())

    def test_normalize_coerces_and_clamps(self) -> None:
        f = Feature("trust", IntType(0, 5))
        assert f.normalize(10) == 5

    def test_normalize_error_names_the_feature(self) -> None:
        f = Feature("trust", IntType())
        with pytest.raises(FeatureValueError, match="trust"):
            f.normalize("nope")

    def test_is_immutable(self) -> None:
        f = Feature("trust", IntType())
        with pytest.raises(FrozenInstanceError):
            f.default = 3  # type: ignore[misc]
