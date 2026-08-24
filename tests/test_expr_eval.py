"""Tests for the evaluator's semantics, driven through a simple dict-backed
environment so the language is exercised independently of the World."""

import pytest

from phrasewood import Environment, EvaluationError, UnknownFeature, evaluate, execute
from phrasewood.expr.nodes import Value


class DictEnv(Environment):
    """A minimal Environment backed by a plain dict, for testing the language."""

    def __init__(self, values: dict[str, Value] | None = None) -> None:
        self.values: dict[str, Value] = dict(values or {})

    def get(self, name: str) -> Value:
        if name not in self.values:
            raise UnknownFeature(f"no feature named {name!r}")
        return self.values[name]

    def set(self, name: str, value: Value) -> None:
        self.values[name] = value


class TestArithmetic:
    def test_precedence_and_grouping(self) -> None:
        assert evaluate("2 + 3 * 4", DictEnv()) == 14
        assert evaluate("(2 + 3) * 4", DictEnv()) == 20

    def test_floor_division(self) -> None:
        assert evaluate("7 / 2", DictEnv()) == 3
        assert evaluate("(0 - 7) / 2", DictEnv()) == -4  # floors toward -inf

    def test_division_by_zero(self) -> None:
        with pytest.raises(EvaluationError, match="division by zero"):
            evaluate("1 / 0", DictEnv())

    def test_arithmetic_rejects_non_integers(self) -> None:
        with pytest.raises(EvaluationError):
            evaluate("'a' + 1", DictEnv())
        with pytest.raises(EvaluationError):
            evaluate("true + 1", DictEnv())


class TestComparisons:
    def test_ordered(self) -> None:
        env = DictEnv({"trust": 5})
        assert evaluate("trust >= 3", env) is True
        assert evaluate("trust < 3", env) is False

    def test_equality(self) -> None:
        assert evaluate("3 == 3", DictEnv()) is True
        assert evaluate("'warm' == 'warm'", DictEnv()) is True
        assert evaluate("'warm' != 'cold'", DictEnv()) is True

    def test_bool_is_distinct_from_int_in_equality(self) -> None:
        assert evaluate("true == 1", DictEnv()) is False
        assert evaluate("true == true", DictEnv()) is True

    def test_ordered_comparison_requires_integers(self) -> None:
        with pytest.raises(EvaluationError):
            evaluate("true < 2", DictEnv())


class TestBooleanLogic:
    def test_and_or_not(self) -> None:
        assert evaluate("true and false", DictEnv()) is False
        assert evaluate("true or false", DictEnv()) is True
        assert evaluate("not true", DictEnv()) is False

    def test_and_short_circuits(self) -> None:
        # `missing` is undefined; if the right side were evaluated this would raise.
        assert evaluate("false and missing >= 1", DictEnv()) is False

    def test_or_short_circuits(self) -> None:
        assert evaluate("true or missing >= 1", DictEnv()) is True

    def test_logic_requires_booleans(self) -> None:
        with pytest.raises(EvaluationError):
            evaluate("1 and 2", DictEnv())


class TestReferences:
    def test_unknown_name_propagates(self) -> None:
        with pytest.raises(UnknownFeature):
            evaluate("missing", DictEnv())

    def test_attribute_access_unsupported_by_default(self) -> None:
        with pytest.raises(EvaluationError, match="no entities"):
            evaluate("ferryman.mood", DictEnv())


class TestEffects:
    def test_plain_assignment(self) -> None:
        env = DictEnv()
        execute("x = 5", env)
        assert env.values["x"] == 5

    def test_increment_and_decrement(self) -> None:
        env = DictEnv({"x": 1})
        execute("x += 2", env)
        assert env.values["x"] == 3
        execute("x -= 5", env)
        assert env.values["x"] == -2

    def test_statements_run_in_order(self) -> None:
        env = DictEnv()
        execute("x = 1; y = x + 2", env)
        assert env.values == {"x": 1, "y": 3}

    def test_increment_requires_integer_state(self) -> None:
        with pytest.raises(EvaluationError):
            execute("x += 1", DictEnv({"x": "text"}))

    def test_attribute_assignment_unsupported_by_default(self) -> None:
        with pytest.raises(EvaluationError, match="no entities"):
            execute("ferryman.mood = 'warm'", DictEnv())
