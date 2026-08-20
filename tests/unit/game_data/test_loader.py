import pytest

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.game_data.loader import LoadedGameData, load_game_data
from teyvat_vision.game_data.records import (
    ArtifactSetDefinition,
    CharacterDefinition,
    MaterialDefinition,
    WeaponDefinition,
)
from teyvat_vision.game_data.source import GameDataSource


class Provider:
    def version(self) -> str:
        return "6.8"

    def characters(self) -> tuple[CharacterDefinition, ...]:
        return (
            CharacterDefinition(
                identity=CanonicalId(
                    kind=EntityKind.CHARACTER,
                    key="10000002",
                )
            ),
        )

    def weapons(self) -> tuple[WeaponDefinition, ...]:
        return (
            WeaponDefinition(
                identity=CanonicalId(
                    kind=EntityKind.WEAPON,
                    key="11509",
                )
            ),
        )

    def artifact_sets(self) -> tuple[ArtifactSetDefinition, ...]:
        return (
            ArtifactSetDefinition(
                identity=CanonicalId(
                    kind=EntityKind.ARTIFACT_SET,
                    key="15001",
                )
            ),
        )

    def materials(self) -> tuple[MaterialDefinition, ...]:
        return (
            MaterialDefinition(
                identity=CanonicalId(
                    kind=EntityKind.MATERIAL,
                    key="104003",
                )
            ),
        )


class DuplicateCharacterProvider(Provider):
    def characters(self) -> tuple[CharacterDefinition, ...]:
        definition = CharacterDefinition(
            identity=CanonicalId(
                kind=EntityKind.CHARACTER,
                key="10000002",
            )
        )

        return (
            definition,
            definition,
        )


def source(
    *,
    version: str = "6.8",
    revision: str | None = "abc123",
) -> GameDataSource:
    return GameDataSource(
        provider="test-provider",
        version=version,
        revision=revision,
    )


def test_load_game_data_returns_loaded_game_data() -> None:
    loaded = load_game_data(
        Provider(),
        source(),
    )

    assert isinstance(loaded, LoadedGameData)


def test_load_game_data_preserves_source_metadata() -> None:
    metadata = source()

    loaded = load_game_data(
        Provider(),
        metadata,
    )

    assert loaded.source == metadata


def test_load_game_data_builds_static_dataset_from_provider() -> None:
    loaded = load_game_data(
        Provider(),
        source(),
    )

    assert loaded.data.version == "6.8"
    assert len(loaded.data.characters) == 1
    assert len(loaded.data.weapons) == 1
    assert len(loaded.data.artifact_sets) == 1
    assert len(loaded.data.materials) == 1


def test_load_game_data_preserves_canonical_character_identity() -> None:
    loaded = load_game_data(
        Provider(),
        source(),
    )

    assert loaded.data.characters[0].identity == CanonicalId(
        kind=EntityKind.CHARACTER,
        key="10000002",
    )


def test_load_game_data_preserves_canonical_weapon_identity() -> None:
    loaded = load_game_data(
        Provider(),
        source(),
    )

    assert loaded.data.weapons[0].identity == CanonicalId(
        kind=EntityKind.WEAPON,
        key="11509",
    )


def test_load_game_data_preserves_canonical_artifact_set_identity() -> None:
    loaded = load_game_data(
        Provider(),
        source(),
    )

    assert loaded.data.artifact_sets[0].identity == CanonicalId(
        kind=EntityKind.ARTIFACT_SET,
        key="15001",
    )


def test_load_game_data_preserves_canonical_material_identity() -> None:
    loaded = load_game_data(
        Provider(),
        source(),
    )

    assert loaded.data.materials[0].identity == CanonicalId(
        kind=EntityKind.MATERIAL,
        key="104003",
    )


def test_load_game_data_rejects_source_version_mismatch() -> None:
    with pytest.raises(ValueError, match="version"):
        load_game_data(
            Provider(),
            source(version="6.7"),
        )


def test_load_game_data_propagates_static_dataset_validation() -> None:
    with pytest.raises(ValueError, match="duplicate character"):
        load_game_data(
            DuplicateCharacterProvider(),
            source(),
        )


def test_load_game_data_allows_source_without_revision() -> None:
    loaded = load_game_data(
        Provider(),
        source(revision=None),
    )

    assert loaded.source.revision is None
