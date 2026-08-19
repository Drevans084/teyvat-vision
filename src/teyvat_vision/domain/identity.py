"""Canonical identity primitives for Teyvat Vision.

Canonical identities are stable machine identities used inside the domain
model. Provider-specific keys, localized names, and user-assigned names are
kept separate from canonical identity.
"""

from dataclasses import dataclass
from enum import StrEnum


class EntityKind(StrEnum):
    """Kinds of game entities that may have canonical identities."""

    CHARACTER = "character"
    WEAPON = "weapon"
    ARTIFACT_SET = "artifact_set"
    MATERIAL = "material"


@dataclass(frozen=True, slots=True)
class CanonicalId:
    """A typed, case-preserving canonical machine identity.

    Keys are intentionally treated as opaque strings. Teyvat Vision does not
    lowercase, case-fold, slugify, or otherwise rewrite them.
    """

    kind: EntityKind
    key: str

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ValueError("key must not be empty")

        if self.key != self.key.strip():
            raise ValueError("key must not contain surrounding whitespace")

    def __str__(self) -> str:
        return f"{self.kind.value}:{self.key}"
