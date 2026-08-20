"""Validated provider-independent static game-data dataset."""

from dataclasses import dataclass

from teyvat_vision.game_data.records import (
    ArtifactSetDefinition,
    CharacterDefinition,
    MaterialDefinition,
    WeaponDefinition,
)


@dataclass(frozen=True, slots=True)
class StaticGameData:
    """One normalized static game-data version."""

    version: str
    characters: tuple[CharacterDefinition, ...]
    weapons: tuple[WeaponDefinition, ...]
    artifact_sets: tuple[ArtifactSetDefinition, ...]
    materials: tuple[MaterialDefinition, ...]

    def __post_init__(self) -> None:
        if not self.version.strip():
            raise ValueError("version must not be blank")

        if self.version != self.version.strip():
            raise ValueError("version must not contain surrounding whitespace")

        self._validate_unique_characters()
        self._validate_unique_weapons()
        self._validate_unique_artifact_sets()
        self._validate_unique_materials()

    def _validate_unique_characters(self) -> None:
        identities = tuple(definition.identity for definition in self.characters)

        if len(set(identities)) != len(identities):
            raise ValueError("duplicate character identity in static game data")

    def _validate_unique_weapons(self) -> None:
        identities = tuple(definition.identity for definition in self.weapons)

        if len(set(identities)) != len(identities):
            raise ValueError("duplicate weapon identity in static game data")

    def _validate_unique_artifact_sets(self) -> None:
        identities = tuple(definition.identity for definition in self.artifact_sets)

        if len(set(identities)) != len(identities):
            raise ValueError("duplicate artifact set identity in static game data")

    def _validate_unique_materials(self) -> None:
        identities = tuple(definition.identity for definition in self.materials)

        if len(set(identities)) != len(identities):
            raise ValueError("duplicate material identity in static game data")
