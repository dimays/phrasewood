"""The mutable, per-playthrough state of a Phrasewood game.

The authored definitions live in :mod:`phrasewood.core`; this package holds what
changes as someone plays — starting with the :class:`World`.
"""

from __future__ import annotations

from phrasewood.state.environment import WorldEnvironment
from phrasewood.state.world import World

__all__ = ["World", "WorldEnvironment"]
