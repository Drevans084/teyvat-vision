"""Weapon domain model for Teyvat Vision.

Weapon objects represent validated account state. Each owned weapon has an
instance identity separate from its shared canonical game-definition identity.
"""

from dataclasses import dataclass

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.domain.instance_identity import OwnedItemId


@dataclass(frozen=True, slots=True)
class Weapon:
    """Canonical state for one account-owned weapon instance."""

    identity: OwnedItemId
    level: int
    ascension: int
    refinement: int
    locked: bool
    equipped_to: CanonicalId | None = None

    def __post_init__(self) -> None:
        if self.identity.definition.kind is not EntityKind.WEAPON:
            raise ValueError("weapon identity definition must have EntityKind.WEAPON")

        if not 1 <= self.level <= 90:
            raise ValueError("level must be between 1 and 90")

        if not 0 <= self.ascension <= 6:
            raise ValueError("ascension must be between 0 and 6")

        if not 1 <= self.refinement <= 5:
            raise ValueError("refinement must be between 1 and 5")

        if type(self.locked) is not bool:
            raise ValueError("locked must be a boolean")

        if self.equipped_to is not None and self.equipped_to.kind is not EntityKind.CHARACTER:
            raise ValueError("equipped_to must reference a character identity")
