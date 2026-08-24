"""Selectors — the policy for which bud blooms when several are eligible.

This is the pluggable seam for storylet *sequencing*. When play reaches an open
moment (no explicit ``goto``) and more than one bud qualifies, the engine asks a
:class:`Selector` what to do. A selector either **names the bud to bloom** (an
automatic policy) or **returns None to defer to the player** (a menu).

Two built-ins ship today; the model is designed so weighted-random, salience, or
deck-based policies — and author-written ones — can join later without touching
the engine.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from phrasewood.core.bud import Bud
    from phrasewood.state.world import World


class Selector(ABC):
    """Chooses among the currently eligible buds."""

    @abstractmethod
    def select(self, eligible: Sequence[Bud], world: World) -> Bud | None:
        """Return the bud to bloom, or None to let the player pick from the menu.

        ``eligible`` is non-empty and in tree (definition) order.
        """


class PrioritySelector(Selector):
    """The first eligible bud in tree order blooms. Deterministic and guided."""

    def select(self, eligible: Sequence[Bud], world: World) -> Bud | None:
        return eligible[0]


class MenuSelector(Selector):
    """Always defer to the player: the eligible buds are offered as a menu."""

    def select(self, eligible: Sequence[Bud], world: World) -> Bud | None:
        return None


__all__ = ["Selector", "PrioritySelector", "MenuSelector"]
