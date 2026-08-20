"""Static game-data provider contract for Teyvat Vision."""

from typing import Protocol, runtime_checkable

from teyvat_vision.game_data.records import (
    ArtifactSetDefinition,
    CharacterDefinition,
    MaterialDefinition,
    WeaponDefinition,
)


@runtime_checkable
class GameDataProvider(Protocol):
    """Provider boundary for canonical static game data."""

    def version(self) -> str:
        """Return the provider's upstream game-data version."""

    def characters(self) -> tuple[CharacterDefinition, ...]:
        """Return canonical character definitions."""

    def weapons(self) -> tuple[WeaponDefinition, ...]:
        """Return canonical weapon definitions."""

    def artifact_sets(self) -> tuple[ArtifactSetDefinition, ...]:
        """Return canonical artifact-set definitions."""

    def materials(self) -> tuple[MaterialDefinition, ...]:
        """Return canonical material definitions."""
