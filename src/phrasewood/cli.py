"""The ``phrasewood`` command line.

For now it launches the bundled example game. Once the ``.pwood`` loader lands
(Phase 2), this grows an argument for a project path to play.
"""

from __future__ import annotations

from phrasewood.engine.play import play
from phrasewood.examples import lamplighter


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``phrasewood`` console script and ``python -m phrasewood``."""
    play(lamplighter())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
