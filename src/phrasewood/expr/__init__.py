"""The Phrasewood expression & effect language.

A tiny, safe language behind a bud's ``when`` (a requirement expression) and
``do`` (a sequence of effects). It is intentionally minimal and fully specified,
so the same syntax evaluates identically here and in the future browser runtime.

Typical use is two-stage: ``parse_expression`` / ``parse_effect`` once (the
result can be cached on a bud), then ``eval_expression`` / ``run_effect`` many
times during play. ``evaluate`` / ``execute`` combine both for convenience.
"""

from __future__ import annotations

from phrasewood.expr.environment import Environment
from phrasewood.expr.evaluator import (
    eval_expression,
    evaluate,
    execute,
    run_effect,
)
from phrasewood.expr.parser import parse_effect, parse_expression

__all__ = [
    "Environment",
    "parse_expression",
    "parse_effect",
    "eval_expression",
    "run_effect",
    "evaluate",
    "execute",
]
