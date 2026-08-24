"""The tokenizer — turns a source string into a flat list of tokens.

This is the first stage: before the parser can reason about grammar rules, the
raw characters ``"trust >= 3"`` become ``[NAME("trust"), GE, INT(3), EOF]``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from phrasewood.errors import ExpressionError
from phrasewood.expr.nodes import Value


class TokenKind(Enum):
    INT = auto()
    STRING = auto()
    NAME = auto()
    # keyword literals / operators
    TRUE = auto()
    FALSE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    # symbols
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    EQ = auto()
    NE = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()
    ASSIGN = auto()
    PLUS_ASSIGN = auto()
    MINUS_ASSIGN = auto()
    LPAREN = auto()
    RPAREN = auto()
    DOT = auto()
    SEMICOLON = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    kind: TokenKind
    value: Value | None
    pos: int


_KEYWORDS: dict[str, TokenKind] = {
    "true": TokenKind.TRUE,
    "false": TokenKind.FALSE,
    "and": TokenKind.AND,
    "or": TokenKind.OR,
    "not": TokenKind.NOT,
}

# Two-character symbols must be tried before their single-character prefixes.
_TWO_CHAR: dict[str, TokenKind] = {
    "==": TokenKind.EQ,
    "!=": TokenKind.NE,
    "<=": TokenKind.LE,
    ">=": TokenKind.GE,
    "+=": TokenKind.PLUS_ASSIGN,
    "-=": TokenKind.MINUS_ASSIGN,
}

_ONE_CHAR: dict[str, TokenKind] = {
    "+": TokenKind.PLUS,
    "-": TokenKind.MINUS,
    "*": TokenKind.STAR,
    "/": TokenKind.SLASH,
    "<": TokenKind.LT,
    ">": TokenKind.GT,
    "=": TokenKind.ASSIGN,
    "(": TokenKind.LPAREN,
    ")": TokenKind.RPAREN,
    ".": TokenKind.DOT,
    ";": TokenKind.SEMICOLON,
}


def tokenize(source: str) -> list[Token]:
    """Break ``source`` into tokens, ending with an ``EOF`` token."""
    tokens: list[Token] = []
    i = 0
    n = len(source)

    while i < n:
        c = source[i]

        if c.isspace():
            i += 1
            continue

        if c.isdigit():
            start = i
            while i < n and source[i].isdigit():
                i += 1
            tokens.append(Token(TokenKind.INT, int(source[start:i]), start))
            continue

        if c in ("'", '"'):
            start = i
            i += 1
            chars: list[str] = []
            while i < n and source[i] != c:
                chars.append(source[i])
                i += 1
            if i >= n:
                raise ExpressionError(f"unterminated string starting at position {start}")
            i += 1  # closing quote
            tokens.append(Token(TokenKind.STRING, "".join(chars), start))
            continue

        if c.isalpha() or c == "_":
            start = i
            while i < n and (source[i].isalnum() or source[i] == "_"):
                i += 1
            word = source[start:i]
            kind = _KEYWORDS.get(word, TokenKind.NAME)
            value = word if kind is TokenKind.NAME else None
            tokens.append(Token(kind, value, start))
            continue

        pair = source[i : i + 2]
        if pair in _TWO_CHAR:
            tokens.append(Token(_TWO_CHAR[pair], None, i))
            i += 2
            continue

        if c in _ONE_CHAR:
            tokens.append(Token(_ONE_CHAR[c], None, i))
            i += 1
            continue

        raise ExpressionError(f"unexpected character {c!r} at position {i}")

    tokens.append(Token(TokenKind.EOF, None, n))
    return tokens


__all__ = ["TokenKind", "Token", "tokenize"]
