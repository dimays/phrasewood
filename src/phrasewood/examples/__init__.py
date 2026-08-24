"""Bundled example games, authored in Python against the engine.

These ship with the package so there is always something real to play, and so the
engine has worked examples to exercise. Until the ``.pwood`` loader lands
(Phase 2), this is how a game reaches the terminal player.
"""

from __future__ import annotations

from phrasewood.examples.lamplighter import tree as lamplighter

__all__ = ["lamplighter"]
