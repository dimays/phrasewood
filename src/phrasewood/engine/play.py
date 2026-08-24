"""The terminal player — play a tree at a text prompt.

A thin loop over :class:`Session`: render the current view, read a numbered
choice, advance, repeat until the story ends. Input and output are injected
(defaulting to ``input``/``print``), so the whole loop is testable by feeding a
script of choices and inspecting the transcript.
"""

from __future__ import annotations

from collections.abc import Callable

from phrasewood.core.tree import Tree
from phrasewood.engine.session import Session, View

# A reader returns the next line of input, or None to quit (EOF / "q").
Reader = Callable[[], "str | None"]
Writer = Callable[[str], None]


def play(
    source: Tree | Session,
    *,
    read: Reader | None = None,
    write: Writer = print,
) -> Session:
    """Play a tree (or resume a session) at the terminal. Returns the session."""
    reader = read if read is not None else _default_read
    session = source if isinstance(source, Session) else Session(source)

    write(f"— {session.tree.title or session.tree.id} —")

    while True:
        view = session.view()
        _render(view, write)
        if view.kind == "end":
            return session
        index = _prompt(view, reader, write)
        if index is None:
            write("")
            write("(you slip back out of the wood)")
            return session
        session.choose(index)


def _render(view: View, write: Writer) -> None:
    write("")
    if view.content:
        write(view.content)
        write("")
    if view.kind == "menu":
        write("Where do you turn?")
    for number, option in enumerate(view.options, start=1):
        write(f"  {number}. {option}")
    if view.kind == "end":
        write("— the end —")


def _prompt(view: View, read: Reader, write: Writer) -> int | None:
    count = len(view.options)
    while True:
        write("")
        raw = read()
        if raw is None:
            return None
        text = raw.strip().lower()
        if text in {"q", "quit", "exit"}:
            return None
        if text.isdigit() and 1 <= int(text) <= count:
            return int(text) - 1
        write(f"Please choose 1–{count} (or 'q' to quit).")


def _default_read() -> str | None:
    try:
        return input("> ")
    except (EOFError, KeyboardInterrupt):
        return None


__all__ = ["play"]
