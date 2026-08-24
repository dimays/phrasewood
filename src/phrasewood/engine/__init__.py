"""The engine — the bloom loop that turns a Tree and a World into play.

:class:`Session` drives a playthrough; a :class:`Selector` decides which bud
blooms when several are eligible (the pluggable sequencing policy).
"""

from __future__ import annotations

from phrasewood.engine.selector import MenuSelector, PrioritySelector, Selector
from phrasewood.engine.session import Session, View

__all__ = [
    "Session",
    "View",
    "Selector",
    "PrioritySelector",
    "MenuSelector",
]
