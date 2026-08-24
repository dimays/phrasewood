"""The AST — the tree a parsed expression or effect becomes.

Each node is a small, immutable record. The parser builds these; the evaluator
walks them. Keeping the tree this plain is what lets the future TypeScript
runtime mirror it exactly.
"""

from __future__ import annotations

from dataclasses import dataclass

# The only value types a Phrasewood world holds. (bool is a subclass of int in
# Python, so the evaluator checks for it explicitly where the distinction matters.)
Value = int | bool | str


# -- expressions -----------------------------------------------------------


@dataclass(frozen=True)
class Literal:
    """A constant: ``3``, ``'warm'``, ``true``."""

    value: Value


@dataclass(frozen=True)
class Name:
    """A bare reference to a world feature: ``trust``."""

    name: str


@dataclass(frozen=True)
class Attr:
    """A reference to an entity's feature: ``ferryman.mood``."""

    target: str
    attr: str


@dataclass(frozen=True)
class Arith:
    """Integer arithmetic: ``+ - * /``."""

    op: str
    left: Expr
    right: Expr


@dataclass(frozen=True)
class Compare:
    """A comparison: ``== != < <= > >=``. Always evaluates to a bool."""

    op: str
    left: Expr
    right: Expr


@dataclass(frozen=True)
class Logical:
    """A short-circuiting ``and`` / ``or``."""

    op: str
    left: Expr
    right: Expr


@dataclass(frozen=True)
class Not:
    """Boolean negation."""

    operand: Expr


# A reference is the subset of expressions you can also assign to.
Reference = Name | Attr

Expr = Literal | Name | Attr | Arith | Compare | Logical | Not


# -- effects ---------------------------------------------------------------


@dataclass(frozen=True)
class Assign:
    """One statement: ``ref = expr`` / ``ref += expr`` / ``ref -= expr``."""

    ref: Reference
    op: str
    value: Expr


@dataclass(frozen=True)
class Effect:
    """A sequence of statements separated by ``;``."""

    statements: tuple[Assign, ...]


__all__ = [
    "Value",
    "Literal",
    "Name",
    "Attr",
    "Arith",
    "Compare",
    "Logical",
    "Not",
    "Reference",
    "Expr",
    "Assign",
    "Effect",
]
