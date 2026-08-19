"""Artifact domain model for Teyvat Vision.

Artifact objects represent validated account state. Static game-rule validation
belongs in the game-data layer rather than being hardcoded here.
"""

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite

from teyvat_vision.domain.identity import CanonicalId, EntityKind


class ArtifactSlot(StrEnum):
    """Canonical artifact equipment slots."""

    FLOWER = "flower"
    PLUME = "plume"
    SANDS = "sands"
    GOBLET = "goblet"
    CIRCLET = "circlet"


@dataclass(frozen=True, slots=True)
class StatValue:
    """A canonical stat key paired with its numeric value."""

    key: str
    value: float

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ValueError("key must not be empty")

        if self.key != self.key.strip():
            raise ValueError("key must not contain surrounding whitespace")

        if not isfinite(self.value):
            raise ValueError("stat value must be finite")


@dataclass(frozen=True, slots=True)
class Artifact:
    """Canonical state for one account-owned artifact."""

    set_identity: CanonicalId
    slot: ArtifactSlot
    rarity: int
    level: int
    main_stat: StatValue
    substats: tuple[StatValue, ...]
    locked: bool
    equipped_to: CanonicalId | None = None

    def __post_init__(self) -> None:
        if self.set_identity.kind is not EntityKind.ARTIFACT_SET:
            raise ValueError("artifact set identity must have EntityKind.ARTIFACT_SET")

        if not 1 <= self.rarity <= 5:
            raise ValueError("rarity must be between 1 and 5")

        if not 0 <= self.level <= 20:
            raise ValueError("level must be between 0 and 20")

        if type(self.locked) is not bool:
            raise ValueError("locked must be a boolean")

        if self.equipped_to is not None and self.equipped_to.kind is not EntityKind.CHARACTER:
            raise ValueError("equipped_to must reference a character identity")

        if len(self.substats) > 4:
            raise ValueError("artifact cannot have more than four substats")

        substat_keys = tuple(substat.key for substat in self.substats)

        if len(set(substat_keys)) != len(substat_keys):
            raise ValueError("artifact cannot contain duplicate substat keys")

        if self.main_stat.key in substat_keys:
            raise ValueError("artifact main stat cannot also appear as a substat")
