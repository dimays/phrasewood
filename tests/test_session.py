"""Tests for the Session bloom loop."""

import pytest

from phrasewood import (
    Bud,
    Choice,
    Feature,
    IntType,
    MenuSelector,
    PrioritySelector,
    Session,
    Tree,
)


class TestBranching:
    def test_choice_runs_effect_and_follows_goto(self) -> None:
        tree = Tree(
            "t",
            features=(Feature("trust", IntType(0, 5), default=0),),
            buds=(
                Bud(
                    "start",
                    content="Start.",
                    once=True,
                    choices=(Choice("gain", do="trust += 2", goto="next"),),
                ),
                Bud("next", content="Next."),
            ),
            start="start",
        )
        session = Session(tree)

        view = session.view()
        assert view.kind == "bud"
        assert view.bud_id == "start"
        assert view.options == ("gain",)

        view = session.choose(0)
        assert session.world.get("trust") == 2
        assert view.kind == "end"
        assert view.content == "Next."

    def test_choice_condition_hides_unavailable_options(self) -> None:
        tree = Tree(
            "t",
            features=(Feature("trust", IntType(0, 5), default=0),),
            buds=(
                Bud(
                    "start",
                    once=True,
                    choices=(Choice("open"), Choice("locked", when="trust >= 5")),
                ),
            ),
            start="start",
        )
        assert Session(tree).view().options == ("open",)


class TestLeavesAndEndings:
    def test_leaf_with_no_successors_ends_showing_its_content(self) -> None:
        tree = Tree("t", buds=(Bud("only", content="The end.", once=True),), start="only")
        session = Session(tree)
        assert session.is_over()
        assert session.view().kind == "end"
        assert session.view().content == "The end."

    def test_leaf_with_a_successor_offers_continue(self) -> None:
        tree = Tree(
            "t",
            buds=(Bud("a", content="A.", once=True), Bud("b", content="B.", once=True)),
            start="a",
        )
        session = Session(tree)
        view = session.view()
        assert view.content == "A."
        assert view.options == ("Continue",)

        view = session.choose(0)  # continue -> only b eligible -> auto-bloom -> leaf -> end
        assert view.kind == "end"
        assert view.content == "B."

    def test_choose_out_of_range_raises(self) -> None:
        tree = Tree("t", buds=(Bud("only", once=True),), start="only")
        with pytest.raises(IndexError):
            Session(tree).choose(0)


class TestSelectionPolicies:
    def _hub_tree(self) -> Tree:
        return Tree(
            "t",
            buds=(
                Bud("hub", content="Hub.", once=True),
                Bud("x", title="Option X", content="X.", once=True),
                Bud("y", title="Option Y", content="Y.", once=True),
            ),
            start="hub",
        )

    def test_menu_offers_eligible_buds_by_title(self) -> None:
        session = Session(self._hub_tree(), selector=MenuSelector())
        view = session.choose(0)  # continue past the hub
        assert view.kind == "menu"
        assert set(view.options) == {"Option X", "Option Y"}

        view = session.choose(0)  # pick one from the menu
        assert view.kind == "bud"
        assert view.content in ("X.", "Y.")

    def test_priority_auto_blooms_without_a_menu(self) -> None:
        session = Session(self._hub_tree(), selector=PrioritySelector())
        view = session.choose(0)  # continue past the hub -> first eligible in tree order
        assert view.kind == "bud"
        assert view.content == "X."

    def test_no_start_begins_with_selection(self) -> None:
        tree = Tree(
            "t",
            buds=(
                Bud("x", title="X", content="X.", once=True),
                Bud("y", title="Y", content="Y.", once=True),
            ),
        )
        assert Session(tree, selector=MenuSelector()).view().kind == "menu"


class TestBloomHistory:
    def test_blooming_is_recorded(self) -> None:
        tree = Tree("t", buds=(Bud("a", content="A.", once=True),), start="a")
        session = Session(tree)
        assert session.world.has_bloomed("a")
        assert session.world.bloom_count("a") == 1
