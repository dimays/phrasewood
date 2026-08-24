"""Buds — the units of story that bloom when the world allows.

A :class:`Bud` carries prose plus the ways out of it: :class:`Choice` options
(tapped) and :class:`Action` verbs (typed at the phrase line). Each bud, choice,
and action may carry a ``when`` requirement and a ``do`` effect, written in the
Phrasewood expression language.

Those ``when`` / ``do`` strings are **compiled once, at construction** — a syntax
error surfaces immediately (not mid-play), and the cached AST is what the engine
evaluates. The original source strings are kept too, so a tree round-trips back
to ``.pwood`` unchanged. By convention: ``when`` / ``do`` are the human-written
source; ``condition`` / ``effect`` are their compiled forms.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from phrasewood.errors import ExpressionError, PhrasewoodError
from phrasewood.expr.nodes import Effect, Expr
from phrasewood.expr.parser import parse_effect, parse_expression


def _compile_condition(source: str | None, where: str) -> Expr | None:
    """Parse a ``when`` string, or return None for 'always'. Adds context on error."""
    if source is None or not source.strip():
        return None
    try:
        return parse_expression(source)
    except ExpressionError as exc:
        raise ExpressionError(f"{where}: {exc}") from exc


def _compile_effect(source: str | None, where: str) -> Effect | None:
    """Parse a ``do`` string, or return None for 'no effect'. Adds context on error."""
    if source is None or not source.strip():
        return None
    try:
        return parse_effect(source)
    except ExpressionError as exc:
        raise ExpressionError(f"{where}: {exc}") from exc


@dataclass(frozen=True)
class Choice:
    """A tappable option out of a bud: a label, an optional gate, effect, and target."""

    label: str
    when: str | None = None
    do: str | None = None
    goto: str | None = None
    condition: Expr | None = field(init=False, compare=False, repr=False, default=None)
    effect: Effect | None = field(init=False, compare=False, repr=False, default=None)

    def __post_init__(self) -> None:
        if not self.label:
            raise PhrasewoodError("a choice needs a non-empty label")
        object.__setattr__(
            self, "condition", _compile_condition(self.when, f"choice {self.label!r} 'when'")
        )
        object.__setattr__(self, "effect", _compile_effect(self.do, f"choice {self.label!r} 'do'"))


@dataclass(frozen=True)
class Action:
    """A phrase-line verb out of a bud: a verb plus the aliases that also match it."""

    verb: str
    aliases: tuple[str, ...] = ()
    when: str | None = None
    do: str | None = None
    goto: str | None = None
    condition: Expr | None = field(init=False, compare=False, repr=False, default=None)
    effect: Effect | None = field(init=False, compare=False, repr=False, default=None)

    def __post_init__(self) -> None:
        if not self.verb:
            raise PhrasewoodError("an action needs a non-empty verb")
        object.__setattr__(self, "aliases", tuple(self.aliases))
        object.__setattr__(
            self, "condition", _compile_condition(self.when, f"action {self.verb!r} 'when'")
        )
        object.__setattr__(self, "effect", _compile_effect(self.do, f"action {self.verb!r} 'do'"))


@dataclass(frozen=True)
class Bud:
    """A unit of story: prose, a requirement, and the choices/actions that leave it."""

    id: str
    content: str = ""
    when: str | None = None
    once: bool = False
    tags: tuple[str, ...] = ()
    choices: tuple[Choice, ...] = ()
    actions: tuple[Action, ...] = ()
    condition: Expr | None = field(init=False, compare=False, repr=False, default=None)

    def __post_init__(self) -> None:
        if not self.id:
            raise PhrasewoodError("a bud needs a non-empty id")
        object.__setattr__(self, "tags", tuple(self.tags))
        object.__setattr__(self, "choices", tuple(self.choices))
        object.__setattr__(self, "actions", tuple(self.actions))
        object.__setattr__(
            self, "condition", _compile_condition(self.when, f"bud {self.id!r} 'when'")
        )

    def gotos(self) -> tuple[str, ...]:
        """Every bud id this bud points at, across its choices and actions."""
        targets = [opt.goto for opt in (*self.choices, *self.actions) if opt.goto]
        return tuple(targets)


__all__ = ["Choice", "Action", "Bud"]
