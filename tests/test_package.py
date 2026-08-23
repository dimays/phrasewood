"""Smoke tests — the package imports and reports a version.

These exist so Phase 0 ships with a green test run; real engine tests arrive
with the model in Phase 1.
"""

import phrasewood


def test_has_version() -> None:
    assert isinstance(phrasewood.__version__, str)
    assert phrasewood.__version__
