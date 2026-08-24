"""The evaluator — walks an AST and produces a value, or applies an effect.

The type rules are deliberately strict and small, so the Python engine and the
future TypeScript runtime can agree exactly:

* arithmetic (``+ - * /``) is integer-only; ``/`` is floor division
* ordered comparisons (``< <= > >=``) are integer-only
* equality (``== !=``) works on any values, but treats a bool as distinct from
  an int (so ``true == 1`` is ``false``)
* ``and`` / ``or`` / ``not`` require booleans and short-circuit
"""

from __future__ import annotations

from phrasewood.errors import EvaluationError
from phrasewood.expr.environment import Environment
from phrasewood.expr.nodes import (
    Arith,
    Assign,
    Attr,
    Compare,
    Effect,
    Expr,
    Literal,
    Logical,
    Name,
    Not,
    Reference,
    Value,
)
from phrasewood.expr.parser import parse_effect, parse_expression


def eval_expression(node: Expr, env: Environment) -> Value:
    """Evaluate a parsed expression against an environment."""
    match node:
        case Literal(value):
            return value
        case Name(name):
            return env.get(name)
        case Attr(target, attr):
            return env.get_attr(target, attr)
        case Not(operand):
            return not _as_bool(eval_expression(operand, env), "not")
        case Logical(op, left, right):
            return _eval_logical(op, left, right, env)
        case Arith(op, left, right):
            return _eval_arith(op, left, right, env)
        case Compare(op, left, right):
            return _eval_compare(op, left, right, env)
    raise EvaluationError(f"cannot evaluate node: {node!r}")  # pragma: no cover


def run_effect(effect: Effect, env: Environment) -> None:
    """Apply each statement of a parsed effect to the environment, in order."""
    for statement in effect.statements:
        _apply(statement, env)


def evaluate(source: str, env: Environment) -> Value:
    """Parse and evaluate an expression string in one step."""
    return eval_expression(parse_expression(source), env)


def execute(source: str, env: Environment) -> None:
    """Parse and apply an effect string in one step."""
    run_effect(parse_effect(source), env)


# -- expression helpers ----------------------------------------------------


def _eval_logical(op: str, left: Expr, right: Expr, env: Environment) -> bool:
    left_value = _as_bool(eval_expression(left, env), op)
    # Short-circuit: don't evaluate the right side when the result is decided.
    if op == "and":
        return _as_bool(eval_expression(right, env), op) if left_value else False
    return True if left_value else _as_bool(eval_expression(right, env), op)


def _eval_arith(op: str, left: Expr, right: Expr, env: Environment) -> int:
    a = _as_int(eval_expression(left, env), op)
    b = _as_int(eval_expression(right, env), op)
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    # op == "/"
    if b == 0:
        raise EvaluationError("division by zero")
    return a // b  # floor division keeps the result an integer


def _eval_compare(op: str, left: Expr, right: Expr, env: Environment) -> bool:
    a = eval_expression(left, env)
    b = eval_expression(right, env)
    if op == "==":
        return _equal(a, b)
    if op == "!=":
        return not _equal(a, b)
    x = _as_int(a, op)
    y = _as_int(b, op)
    if op == "<":
        return x < y
    if op == "<=":
        return x <= y
    if op == ">":
        return x > y
    return x >= y  # op == ">="


def _equal(a: Value, b: Value) -> bool:
    # bool and int are distinct here, so `true == 1` is False rather than True.
    return type(a) is type(b) and a == b


def _as_int(value: Value, op: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise EvaluationError(f"'{op}' needs integers, got {type(value).__name__}: {value!r}")
    return value


def _as_bool(value: Value, op: str) -> bool:
    if not isinstance(value, bool):
        raise EvaluationError(f"'{op}' needs a boolean, got {type(value).__name__}: {value!r}")
    return value


# -- effect helpers --------------------------------------------------------


def _apply(statement: Assign, env: Environment) -> None:
    value = eval_expression(statement.value, env)
    if statement.op == "=":
        _write(env, statement.ref, value)
        return
    current = _as_int(_read(env, statement.ref), statement.op)
    delta = _as_int(value, statement.op)
    _write(env, statement.ref, current + delta if statement.op == "+=" else current - delta)


def _read(env: Environment, ref: Reference) -> Value:
    if isinstance(ref, Name):
        return env.get(ref.name)
    return env.get_attr(ref.target, ref.attr)


def _write(env: Environment, ref: Reference, value: Value) -> None:
    if isinstance(ref, Name):
        env.set(ref.name, value)
    else:
        env.set_attr(ref.target, ref.attr, value)


__all__ = ["eval_expression", "run_effect", "evaluate", "execute"]
