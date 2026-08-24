"""Reading and (later) writing the `.pwood` on-disk format.

`load(path)` turns a project folder or a zipped `.pwood` file into a `Tree`. The
writer lands in a later commit.
"""

from __future__ import annotations

from phrasewood.pwood.load import load

__all__ = ["load"]
