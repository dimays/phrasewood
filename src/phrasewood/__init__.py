"""Phrasewood — an engine for text games grown from buds and features.

Phrasewood is the open-source core beneath the Phrasewood platform: a small
vocabulary — *features* (the world's state), *buds* (moments that bloom when
that state allows), and *entities* (the things, people, and places state hangs
on) — that composes into anything from a five-minute *sprig* to a sprawling
*tree*.

The design vocabulary is fixed in ``DECISIONS.md``; the (draft) on-disk project
format lives in ``docs/pwood-format.md``.
"""

from phrasewood.core import (
    BoolType,
    EnumType,
    Feature,
    FeatureType,
    IntType,
    TextType,
)
from phrasewood.errors import (
    DuplicateFeature,
    FeatureValueError,
    PhrasewoodError,
    UnknownFeature,
)
from phrasewood.state import World

__version__ = "0.0.1"

__all__ = [
    "__version__",
    # features
    "Feature",
    "FeatureType",
    "IntType",
    "BoolType",
    "TextType",
    "EnumType",
    # state
    "World",
    # errors
    "PhrasewoodError",
    "FeatureValueError",
    "UnknownFeature",
    "DuplicateFeature",
]
