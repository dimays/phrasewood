"""Tests for the tokenizer and parser: the shapes they produce, and the
syntax errors they reject."""

import pytest

from phrasewood.errors import ExpressionError
from phrasewood.expr.nodes import (
    Arith,
    Assign,
    Attr,
    Compare,
    Literal,
    Logical,
    Name,
    Not,
)
from phrasewood.expr.parser import parse_effect, parse_expression


class TestAtoms:
    def test_integer(self) -> None:
        assert parse_expression("3") == Literal(3)

    def test_string(self) -> None:
        assert parse_expression("'warm'") == Literal("warm")

    def test_booleans(self) -> None:
        assert parse_expression("true") == Literal(True)
        assert parse_expression("false") == Literal(False)

    def test_name(self) -> None:
        assert parse_expression("trust") == Name("trust")

    def test_entity_attribute(self) -> None:
        assert parse_expression("ferryman.mood") == Attr("ferryman", "mood")


class TestPrecedence:
    def test_times_binds_tighter_than_plus(self) -> None:
        # 2 + 3 * 4  ==  2 + (3 * 4)
        assert parse_expression("2 + 3 * 4") == Arith(
            "+", Literal(2), Arith("*", Literal(3), Literal(4))
        )

    def test_and_binds_tighter_than_or(self) -> None:
        assert parse_expression("a or b and c") == Logical(
            "or", Name("a"), Logical("and", Name("b"), Name("c"))
        )

    def test_comparison_between_boolean_and_arithmetic(self) -> None:
        assert parse_expression("trust >= 3 and has_lantern") == Logical(
            "and", Compare(">=", Name("trust"), Literal(3)), Name("has_lantern")
        )

    def test_parentheses_override_precedence(self) -> None:
        assert parse_expression("(a or b) and c") == Logical(
            "and", Logical("or", Name("a"), Name("b")), Name("c")
        )

    def test_left_associativity(self) -> None:
        # 10 - 3 - 2  ==  (10 - 3) - 2
        assert parse_expression("10 - 3 - 2") == Arith(
            "-", Arith("-", Literal(10), Literal(3)), Literal(2)
        )


class TestNot:
    def test_single(self) -> None:
        assert parse_expression("not lit") == Not(Name("lit"))

    def test_stacked(self) -> None:
        assert parse_expression("not not lit") == Not(Not(Name("lit")))


class TestEffects:
    def test_single_statement(self) -> None:
        assert parse_effect("trust += 2") == parse_effect("trust += 2")
        effect = parse_effect("trust += 2")
        assert effect.statements == (Assign(Name("trust"), "+=", Literal(2)),)

    def test_multiple_statements(self) -> None:
        effect = parse_effect("trust += 2; mood = 'warm'")
        assert effect.statements == (
            Assign(Name("trust"), "+=", Literal(2)),
            Assign(Name("mood"), "=", Literal("warm")),
        )

    def test_assign_to_entity_attribute(self) -> None:
        effect = parse_effect("ferryman.mood = 'warm'")
        assert effect.statements == (Assign(Attr("ferryman", "mood"), "=", Literal("warm")),)

    def test_trailing_semicolon_is_allowed(self) -> None:
        assert len(parse_effect("trust += 1;").statements) == 1

    def test_rhs_can_be_a_full_expression(self) -> None:
        effect = parse_effect("gold = gold + 2 * 3")
        assert effect.statements[0].value == Arith(
            "+", Name("gold"), Arith("*", Literal(2), Literal(3))
        )


class TestSyntaxErrors:
    def test_unterminated_string(self) -> None:
        with pytest.raises(ExpressionError, match="unterminated"):
            parse_expression("'warm")

    def test_unexpected_character(self) -> None:
        with pytest.raises(ExpressionError, match="unexpected character"):
            parse_expression("trust @ 3")

    def test_missing_closing_paren(self) -> None:
        with pytest.raises(ExpressionError):
            parse_expression("(1 + 2")

    def test_empty_expression(self) -> None:
        with pytest.raises(ExpressionError):
            parse_expression("")

    def test_chained_comparison_is_rejected(self) -> None:
        with pytest.raises(ExpressionError):
            parse_expression("1 < 2 < 3")

    def test_effect_needs_an_assignment_operator(self) -> None:
        with pytest.raises(ExpressionError):
            parse_effect("trust 3")

    def test_dangling_operator(self) -> None:
        with pytest.raises(ExpressionError):
            parse_expression("trust +")
