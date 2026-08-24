"""The ``phrasewood`` command line.

phrasewood            # play the bundled example game
phrasewood GAME       # play a .pwood file or project folder
"""

from __future__ import annotations

import argparse

from phrasewood.engine.play import play
from phrasewood.errors import PhrasewoodError
from phrasewood.examples import lamplighter
from phrasewood.pwood import load


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``phrasewood`` console script and ``python -m phrasewood``."""
    parser = argparse.ArgumentParser(prog="phrasewood", description="Play a Phrasewood game.")
    parser.add_argument(
        "game",
        nargs="?",
        help="path to a .pwood file or project folder (default: the bundled example)",
    )
    args = parser.parse_args(argv)

    try:
        tree = load(args.game) if args.game else lamplighter()
    except PhrasewoodError as exc:
        parser.error(str(exc))  # prints a clear message and exits non-zero

    play(tree)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
