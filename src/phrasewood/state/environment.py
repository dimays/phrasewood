"""Adapters that let the expression language read and write game state.

``WorldEnvironment`` bridges the language's :class:`Environment` interface to a
concrete :class:`World`, so a ``when`` or ``do`` string can be evaluated against
live feature values. Entity attribute access joins it when entities land.
"""

from __future__ import annotations

from phrasewood.expr.environment import Environment
from phrasewood.expr.nodes import Value
from phrasewood.state.world import World


class WorldEnvironment(Environment):
    """Resolves feature names against a :class:`World`.

    Assignments go through ``World.set``, so values written by effects are
    validated and clamped by their feature definitions just like any other write.
    """

    def __init__(self, world: World) -> None:
        self._world = world

    def get(self, name: str) -> Value:
        return self._world.get(name)

    def set(self, name: str, value: Value) -> None:
        self._world.set(name, value)


__all__ = ["WorldEnvironment"]
