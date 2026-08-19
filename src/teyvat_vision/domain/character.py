"""Character domain model for Teyvat Vision.

Character objects represent validated account state. Recognition uncertainty
belongs in the recognition layer and must be resolved before constructing a
Character.
"""

from dataclasses import dataclass

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.domain.names import CustomName


@dataclass(frozen=True, slots=True)
class TalentLevels:
    """Base talent levels recorded for a character."""

    normal: int
    skill: int
    burst: int

    def __post_init__(self) -> None:
        if not 1 <= self.normal <= 15:
            raise ValueError("normal talent level must be between 1 and 15")

        if not 1 <= self.skill <= 15:
            raise ValueError("skill talent level must be between 1 and 15")

        if not 1 <= self.burst <= 15:
            raise ValueError("burst talent level must be between 1 and 15")


@dataclass(frozen=True, slots=True)
class Character:
    """Canonical character state belonging to an account snapshot."""

    identity: CanonicalId
    level: int
    ascension: int
    constellation: int
    talents: TalentLevels
    custom_name: CustomName | None = None

    def __post_init__(self) -> None:
        if self.identity.kind is not EntityKind.CHARACTER:
            raise ValueError("character identity must have EntityKind.CHARACTER")

        if not 1 <= self.level <= 100:
            raise ValueError("level must be between 1 and 100")

        if not 0 <= self.ascension <= 6:
            raise ValueError("ascension must be between 0 and 6")

        if not 0 <= self.constellation <= 6:
            raise ValueError("constellation must be between 0 and 6")
