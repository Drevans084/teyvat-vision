"""Canonical account snapshot model for Teyvat Vision.

Snapshot sections explicitly record scan coverage so an empty collection cannot
silently mean both "scanned and empty" and "not scanned."
"""

from dataclasses import dataclass
from enum import StrEnum

from teyvat_vision.domain.artifact import Artifact
from teyvat_vision.domain.character import Character
from teyvat_vision.domain.material import MaterialStack
from teyvat_vision.domain.weapon import Weapon


class SectionStatus(StrEnum):
    """Coverage state for one account snapshot section."""

    COMPLETE = "complete"
    PARTIAL = "partial"
    NOT_SCANNED = "not_scanned"


@dataclass(frozen=True, slots=True)
class SnapshotSection[T]:
    """One typed account section together with its scan coverage state."""

    status: SectionStatus
    items: tuple[T, ...]

    def __post_init__(self) -> None:
        if self.status is SectionStatus.NOT_SCANNED and self.items:
            raise ValueError("not scanned section must not contain items")


@dataclass(frozen=True, slots=True)
class AccountSnapshot:
    """Canonical account state composed from independently scanned sections."""

    characters: SnapshotSection[Character]
    weapons: SnapshotSection[Weapon]
    artifacts: SnapshotSection[Artifact]
    materials: SnapshotSection[MaterialStack]

    def __post_init__(self) -> None:
        self._validate_unique_characters()
        self._validate_unique_materials()
        self._validate_equipment_owners()

    def _validate_unique_characters(self) -> None:
        identities = tuple(character.identity for character in self.characters.items)

        if len(set(identities)) != len(identities):
            raise ValueError("duplicate character identity in account snapshot")

    def _validate_unique_materials(self) -> None:
        identities = tuple(material.identity for material in self.materials.items)

        if len(set(identities)) != len(identities):
            raise ValueError("duplicate material identity in account snapshot")

    def _validate_equipment_owners(self) -> None:
        if self.characters.status is not SectionStatus.COMPLETE:
            return

        character_identities = {character.identity for character in self.characters.items}

        for weapon in self.weapons.items:
            if weapon.equipped_to is not None and weapon.equipped_to not in character_identities:
                raise ValueError(
                    "weapon equipped_to references a character absent from "
                    "the complete character section"
                )

        for artifact in self.artifacts.items:
            if (
                artifact.equipped_to is not None
                and artifact.equipped_to not in character_identities
            ):
                raise ValueError(
                    "artifact equipped_to references a character absent from "
                    "the complete character section"
                )
