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
    EvaluationError,
    ExpressionError,
    FeatureValueError,
    PhrasewoodError,
    UnknownFeature,
)
from phrasewood.expr import (
    Environment,
    eval_expression,
    evaluate,
    execute,
    parse_effect,
    parse_expression,
    run_effect,
)
from phrasewood.state import World, WorldEnvironment

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
    "WorldEnvironment",
    # expression & effect language
    "Environment",
    "parse_expression",
    "parse_effect",
    "eval_expression",
    "run_effect",
    "evaluate",
    "execute",
    # errors
    "PhrasewoodError",
    "FeatureValueError",
    "UnknownFeature",
    "DuplicateFeature",
    "ExpressionError",
    "EvaluationError",
]
