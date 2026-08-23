"""The exception types Phrasewood raises.

Everything inherits from :class:`PhrasewoodError`, so a caller can catch the
whole family with one ``except``. The specific types also inherit from the
closest built-in (``ValueError`` / ``KeyError``-like) where it reads naturally,
so ordinary Python error handling works too.
"""

from __future__ import annotations


class PhrasewoodError(Exception):
    """Base class for every error Phrasewood raises."""


class FeatureValueError(PhrasewoodError, ValueError):
    """A value is not valid for a feature's type or bounds."""


class UnknownFeature(PhrasewoodError):
    """A feature was referenced by a name the world does not define."""


class DuplicateFeature(PhrasewoodError):
    """Two features were defined with the same name."""


__all__ = [
    "PhrasewoodError",
    "FeatureValueError",
    "UnknownFeature",
    "DuplicateFeature",
]
