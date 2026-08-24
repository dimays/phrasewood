"""The Environment — the seam between the language and the state it reads/writes.

The evaluator never touches a ``World`` directly. It only asks an ``Environment``
to resolve a name (or an entity attribute) and to assign to one. That keeps the
language independent of the concrete state model: a ``World`` adapter provides one
implementation today, and entity- or helper-aware environments can plug in later
without changing a line of the evaluator.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from phrasewood.errors import EvaluationError
from phrasewood.expr.nodes import Value


class Environment(ABC):
    """Resolves the names an expression references, and applies assignments."""

    @abstractmethod
    def get(self, name: str) -> Value:
        """Return the current value of a world feature."""

    @abstractmethod
    def set(self, name: str, value: Value) -> None:
        """Set a world feature's value."""

    # Attribute (entity.feature) access is optional. Environments that have no
    # entities inherit these and report a clear error rather than silently failing.

    def get_attr(self, target: str, attr: str) -> Value:
        raise EvaluationError(f"cannot read {target}.{attr}: this environment has no entities")

    def set_attr(self, target: str, attr: str, value: Value) -> None:
        raise EvaluationError(f"cannot set {target}.{attr}: this environment has no entities")


__all__ = ["Environment"]
