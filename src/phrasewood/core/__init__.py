"""The authored, immutable definitions that make up a Phrasewood story.

Everything here describes what an author *wrote* — features, entities, buds, and
the ``Tree`` that binds them. None of it changes during play; the mutable side of
a game lives in :mod:`phrasewood.state`.
"""

from __future__ import annotations

from phrasewood.core.bud import Action, Bud, Choice
from phrasewood.core.entity import Entity
from phrasewood.core.feature import (
    BoolType,
    EnumType,
    Feature,
    FeatureType,
    IntType,
    TextType,
)
from phrasewood.core.tree import Tree

__all__ = [
    "Feature",
    "FeatureType",
    "IntType",
    "BoolType",
    "TextType",
    "EnumType",
    "Entity",
    "Bud",
    "Choice",
    "Action",
    "Tree",
]
