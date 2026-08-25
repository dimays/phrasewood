"""Splitting a bud file into its YAML frontmatter and its Markdown body.

The shape is the familiar Jekyll/Hugo one: a `---`-fenced YAML block at the top,
then the prose beneath. This module only *splits*; the frontmatter is parsed as
YAML by the loader.
"""

from __future__ import annotations

import re

from phrasewood.errors import LoadError

# Opening fence, the frontmatter, a closing fence on its own line, then the body.
# Tolerant of trailing spaces on the fences and of CRLF line endings.
_FRONTMATTER = re.compile(
    r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n?(.*)\Z",
    re.DOTALL,
)


def split_frontmatter(text: str, where: str) -> tuple[str, str]:
    """Return (frontmatter YAML text, body text). Raises if the fences are missing."""
    match = _FRONTMATTER.match(text.lstrip("\ufeff"))  # tolerate a leading BOM
    if match is None:
        raise LoadError(f"{where}: missing '---' YAML frontmatter")
    return match.group(1), match.group(2)


__all__ = ["split_frontmatter"]
