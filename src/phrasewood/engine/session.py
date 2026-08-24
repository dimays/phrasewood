"""The Session — one in-progress playthrough of a tree.

A session ties a :class:`Tree` (the authored story) to a :class:`World` (the
mutable state) and drives the bloom loop:

1. A bud is in **focus**: its prose and available options (choices + actions) are
   shown. The player picks one.
2. Taking an option runs its effect, then either follows its ``goto`` to a named
   bud, or — for an open transition — asks the :class:`Selector` what blooms next.
3. When several buds are eligible and the selector defers, the player is offered a
   **menu** of them. When none are eligible, the story **ends**.

The engine exposes this as a tiny state machine: :meth:`view` describes what to
show, and :meth:`choose` takes the player's pick. The same surface will drive the
terminal player and, later, the browser runtime.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from functools import partial

from phrasewood.core.bud import Action, Bud, Choice
from phrasewood.core.tree import Tree
from phrasewood.engine.selector import MenuSelector, Selector
from phrasewood.expr.evaluator import eval_expression, run_effect
from phrasewood.state.environment import WorldEnvironment
from phrasewood.state.world import World

_Option = Choice | Action


@dataclass(frozen=True)
class View:
    """What to show the player right now.

    ``kind`` is ``"bud"`` (prose + options), ``"menu"`` (pick a bud to bloom), or
    ``"end"`` (the story is over; ``content`` may hold a final passage). ``options``
    are the labels to display, in the order :meth:`Session.choose` indexes them.
    """

    kind: str
    content: str
    options: tuple[str, ...]
    bud_id: str | None = None


class Session:
    def __init__(
        self,
        tree: Tree,
        world: World | None = None,
        selector: Selector | None = None,
    ) -> None:
        self.tree = tree
        self.world = world if world is not None else World.for_tree(tree)
        self.selector = selector if selector is not None else MenuSelector()
        self._env = WorldEnvironment(self.world)
        self._moves: list[Callable[[], None]] = []
        self._view = View("end", "", ())
        self._begin()

    # -- public surface ----------------------------------------------------

    def view(self) -> View:
        """The current view — what the player should see."""
        return self._view

    def is_over(self) -> bool:
        """Whether the story has ended."""
        return self._view.kind == "end"

    def choose(self, index: int) -> View:
        """Take the option at ``index`` in the current view; return the next view."""
        if not 0 <= index < len(self._moves):
            raise IndexError(f"no option {index}; there are {len(self._moves)}")
        self._moves[index]()
        return self._view

    # -- the loop ----------------------------------------------------------

    def _begin(self) -> None:
        if self.tree.start:
            self._bloom(self.tree.bud(self.tree.start))
        else:
            self._select(exclude=None)

    def _bloom(self, bud: Bud) -> None:
        """Bring a bud into focus and build its view."""
        self.world.mark_bloomed(bud.id)
        options = self._available_options(bud)
        if options:
            self._moves = [partial(self._take, option, bud) for option in options]
            labels = tuple(_label(option) for option in options)
            self._view = View("bud", bud.content, labels, bud_id=bud.id)
            return
        # A leaf bud: is there anywhere to go from here?
        if self._eligible(exclude=bud.id):
            self._moves = [partial(self._select, exclude=bud.id)]
            self._view = View("bud", bud.content, ("Continue",), bud_id=bud.id)
        else:
            self._moves = []
            self._view = View("end", bud.content, (), bud_id=bud.id)

    def _take(self, option: _Option, from_bud: Bud) -> None:
        """Apply a chosen option: run its effect, then transition."""
        if option.effect is not None:
            run_effect(option.effect, self._env)
        if option.goto:
            self._bloom(self.tree.bud(option.goto))
        else:
            self._select(exclude=from_bud.id)

    def _select(self, exclude: str | None) -> None:
        """Choose the next bud among eligible ones, per the selector."""
        eligible = self._eligible(exclude=exclude)
        if not eligible:
            self._moves = []
            self._view = View("end", "", ())
            return
        chosen = self.selector.select(eligible, self.world)
        # A menu of one isn't a menu.
        if chosen is None and len(eligible) == 1:
            chosen = eligible[0]
        if chosen is not None:
            self._bloom(chosen)
        else:
            self._moves = [partial(self._bloom, bud) for bud in eligible]
            labels = tuple(_menu_label(bud) for bud in eligible)
            self._view = View("menu", "", labels)

    # -- eligibility -------------------------------------------------------

    def _eligible(self, exclude: str | None) -> list[Bud]:
        """Buds whose condition passes now, minus exhausted and just-left ones."""
        result: list[Bud] = []
        for bud in self.tree.buds:
            if bud.id == exclude:
                continue
            if bud.once and self.world.has_bloomed(bud.id):
                continue
            if bud.condition is None or eval_expression(bud.condition, self._env):
                result.append(bud)
        return result

    def _available_options(self, bud: Bud) -> list[_Option]:
        """The bud's choices then actions whose own condition currently passes."""
        options: list[_Option] = [*bud.choices, *bud.actions]
        return [
            option
            for option in options
            if option.condition is None or eval_expression(option.condition, self._env)
        ]


def _label(option: _Option) -> str:
    return option.label if isinstance(option, Choice) else option.verb


def _menu_label(bud: Bud) -> str:
    return bud.title or bud.id


__all__ = ["Session", "View"]
