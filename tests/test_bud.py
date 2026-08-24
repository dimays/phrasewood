"""Tests for Bud, Choice, and Action — including compile-at-construction."""

import pytest

from phrasewood import Action, Bud, Choice, ExpressionError, PhrasewoodError


class TestChoice:
    def test_requires_a_label(self) -> None:
        with pytest.raises(PhrasewoodError):
            Choice("")

    def test_compiles_when_and_do(self) -> None:
        choice = Choice("go", when="trust >= 3", do="trust += 1", goto="next")
        assert choice.condition is not None
        assert choice.effect is not None
        assert choice.goto == "next"

    def test_missing_when_and_do_compile_to_none(self) -> None:
        choice = Choice("go")
        assert choice.condition is None
        assert choice.effect is None

    def test_bad_when_syntax_fails_with_context(self) -> None:
        with pytest.raises(ExpressionError, match="'when'"):
            Choice("go", when="trust >=")

    def test_bad_do_syntax_fails_with_context(self) -> None:
        with pytest.raises(ExpressionError, match="'do'"):
            Choice("go", do="trust +=")

    def test_equality_ignores_the_compiled_forms(self) -> None:
        assert Choice("go", when="trust >= 1") == Choice("go", when="trust >= 1")


class TestAction:
    def test_requires_a_verb(self) -> None:
        with pytest.raises(PhrasewoodError):
            Action("")

    def test_aliases_normalize_to_a_tuple(self) -> None:
        action = Action("pay", aliases=["give lantern", "offer lantern"])
        assert action.aliases == ("give lantern", "offer lantern")

    def test_compiles_when_and_do(self) -> None:
        action = Action("pay", do="has_lantern = false", goto="crossing")
        assert action.effect is not None
        assert action.goto == "crossing"


class TestBud:
    def test_requires_an_id(self) -> None:
        with pytest.raises(PhrasewoodError):
            Bud("")

    def test_compiles_its_when(self) -> None:
        assert Bud("start", when="chapter == 1").condition is not None
        assert Bud("start").condition is None

    def test_normalizes_collections_to_tuples(self) -> None:
        bud = Bud("start", tags=["intro"], choices=[Choice("go")], actions=[Action("wait")])
        assert isinstance(bud.tags, tuple)
        assert isinstance(bud.choices, tuple)
        assert isinstance(bud.actions, tuple)

    def test_bad_when_syntax_fails_with_context(self) -> None:
        with pytest.raises(ExpressionError, match="bud 'start'"):
            Bud("start", when="chapter ==")

    def test_gotos_collects_targets(self) -> None:
        bud = Bud(
            "start",
            choices=(Choice("a", goto="one"), Choice("b")),
            actions=(Action("c", goto="two"),),
        )
        assert bud.gotos() == ("one", "two")
