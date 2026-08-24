"""Tests for the built-in selectors."""

from phrasewood import Bud, MenuSelector, PrioritySelector, World


def test_priority_picks_the_first_eligible() -> None:
    eligible = [Bud("a"), Bud("b")]
    assert PrioritySelector().select(eligible, World([])).id == "a"


def test_menu_defers_to_the_player() -> None:
    assert MenuSelector().select([Bud("a"), Bud("b")], World([])) is None
