"""The parser — turns a token list into an AST.

This is a hand-written recursive-descent parser: there is one method per grammar
rule (see ``docs/pwood-format.md``), and a rule that refers to another rule just
calls that method. The rules are layered loosest-first (``or`` at the top,
``factor`` at the bottom), which is what encodes operator precedence.
"""

from __future__ import annotations

from phrasewood.errors import ExpressionError
from phrasewood.expr import nodes
from phrasewood.expr.nodes import Assign, Attr, Effect, Expr, Literal, Name, Reference
from phrasewood.expr.tokens import Token, TokenKind, tokenize

_COMPARE_OPS: dict[TokenKind, str] = {
    TokenKind.EQ: "==",
    TokenKind.NE: "!=",
    TokenKind.LT: "<",
    TokenKind.LE: "<=",
    TokenKind.GT: ">",
    TokenKind.GE: ">=",
}
_SUM_OPS: dict[TokenKind, str] = {TokenKind.PLUS: "+", TokenKind.MINUS: "-"}
_TERM_OPS: dict[TokenKind, str] = {TokenKind.STAR: "*", TokenKind.SLASH: "/"}
_ASSIGN_OPS: dict[TokenKind, str] = {
    TokenKind.ASSIGN: "=",
    TokenKind.PLUS_ASSIGN: "+=",
    TokenKind.MINUS_ASSIGN: "-=",
}


class _Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._pos = 0

    # -- token cursor ------------------------------------------------------

    @property
    def _current(self) -> Token:
        return self._tokens[self._pos]

    def _advance(self) -> Token:
        token = self._tokens[self._pos]
        self._pos += 1
        return token

    def _expect(self, kind: TokenKind, what: str) -> Token:
        token = self._current
        if token.kind is not kind:
            raise ExpressionError(f"expected {what} at position {token.pos}")
        return self._advance()

    # -- entry points ------------------------------------------------------

    def parse_expression(self) -> Expr:
        expr = self._or()
        self._expect(TokenKind.EOF, "end of expression")
        return expr

    def parse_effect(self) -> Effect:
        statements = [self._statement()]
        while self._current.kind is TokenKind.SEMICOLON:
            self._advance()
            # allow a trailing ";" with nothing after it
            if self._current.kind is TokenKind.EOF:
                break
            statements.append(self._statement())
        self._expect(TokenKind.EOF, "end of effect")
        return Effect(tuple(statements))

    # -- expression rules (loosest to tightest) ---------------------------

    def _or(self) -> Expr:
        left = self._and()
        while self._current.kind is TokenKind.OR:
            self._advance()
            left = nodes.Logical("or", left, self._and())
        return left

    def _and(self) -> Expr:
        left = self._not()
        while self._current.kind is TokenKind.AND:
            self._advance()
            left = nodes.Logical("and", left, self._not())
        return left

    def _not(self) -> Expr:
        if self._current.kind is TokenKind.NOT:
            self._advance()
            return nodes.Not(self._not())
        return self._comparison()

    def _comparison(self) -> Expr:
        left = self._sum()
        op = _COMPARE_OPS.get(self._current.kind)
        if op is not None:
            self._advance()
            return nodes.Compare(op, left, self._sum())
        return left

    def _sum(self) -> Expr:
        left = self._term()
        while (op := _SUM_OPS.get(self._current.kind)) is not None:
            self._advance()
            left = nodes.Arith(op, left, self._term())
        return left

    def _term(self) -> Expr:
        left = self._factor()
        while (op := _TERM_OPS.get(self._current.kind)) is not None:
            self._advance()
            left = nodes.Arith(op, left, self._factor())
        return left

    def _factor(self) -> Expr:
        token = self._current
        if token.kind is TokenKind.INT or token.kind is TokenKind.STRING:
            self._advance()
            return Literal(token.value)  # type: ignore[arg-type]
        if token.kind is TokenKind.TRUE:
            self._advance()
            return Literal(True)
        if token.kind is TokenKind.FALSE:
            self._advance()
            return Literal(False)
        if token.kind is TokenKind.NAME:
            return self._reference()
        if token.kind is TokenKind.LPAREN:
            self._advance()
            inner = self._or()
            self._expect(TokenKind.RPAREN, "a closing ')'")
            return inner
        raise ExpressionError(f"unexpected token at position {token.pos}")

    # -- shared: a name or entity.attribute reference ----------------------

    def _reference(self) -> Reference:
        name = self._expect(TokenKind.NAME, "a name")
        if self._current.kind is TokenKind.DOT:
            self._advance()
            attr = self._expect(TokenKind.NAME, "a feature name after '.'")
            return Attr(str(name.value), str(attr.value))
        return Name(str(name.value))

    # -- effect rules ------------------------------------------------------

    def _statement(self) -> Assign:
        ref = self._reference()
        op = _ASSIGN_OPS.get(self._current.kind)
        if op is None:
            raise ExpressionError(f"expected '=', '+=', or '-=' at position {self._current.pos}")
        self._advance()
        return Assign(ref, op, self._or())


def parse_expression(source: str) -> Expr:
    """Parse a ``when``-style expression string into an AST."""
    return _Parser(tokenize(source)).parse_expression()


def parse_effect(source: str) -> Effect:
    """Parse a ``do``-style effect string into an AST."""
    return _Parser(tokenize(source)).parse_effect()


__all__ = ["parse_expression", "parse_effect"]
