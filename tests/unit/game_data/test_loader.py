import pytest

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.game_data.assets import AssetRole, GameDataAsset
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

    def source(self) -> GameDataSource:
        return GameDataSource(
            provider="test-provider",
            version="6.8",
            revision="abc123",
        )

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

    def assets(self) -> tuple[GameDataAsset, ...]:
        return (
            GameDataAsset(
                subject=CanonicalId(
                    kind=EntityKind.CHARACTER,
                    key="10000002",
                ),
                role=AssetRole.CHARACTER_ICON,
                reference="UI_AvatarIcon_Ayaka",
            ),
        )


class MismatchedSourceProvider(Provider):
    def source(self) -> GameDataSource:
        return GameDataSource(
            provider="test-provider",
            version="6.7",
            revision="abc123",
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


class NoRevisionProvider(Provider):
    def source(self) -> GameDataSource:
        return GameDataSource(
            provider="test-provider",
            version="6.8",
        )


def test_load_game_data_returns_loaded_game_data() -> None:
    loaded = load_game_data(Provider())

    assert isinstance(loaded, LoadedGameData)


def test_load_game_data_preserves_provider_source_metadata() -> None:
    provider = Provider()

    loaded = load_game_data(provider)

    assert loaded.source == provider.source()


def test_load_game_data_builds_static_dataset_from_provider() -> None:
    loaded = load_game_data(Provider())

    assert loaded.data.version == "6.8"
    assert len(loaded.data.characters) == 1
    assert len(loaded.data.weapons) == 1
    assert len(loaded.data.artifact_sets) == 1
    assert len(loaded.data.materials) == 1


def test_load_game_data_preserves_canonical_character_identity() -> None:
    loaded = load_game_data(Provider())

    assert loaded.data.characters[0].identity == CanonicalId(
        kind=EntityKind.CHARACTER,
        key="10000002",
    )


def test_load_game_data_preserves_canonical_weapon_identity() -> None:
    loaded = load_game_data(Provider())

    assert loaded.data.weapons[0].identity == CanonicalId(
        kind=EntityKind.WEAPON,
        key="11509",
    )


def test_load_game_data_preserves_canonical_artifact_set_identity() -> None:
    loaded = load_game_data(Provider())

    assert loaded.data.artifact_sets[0].identity == CanonicalId(
        kind=EntityKind.ARTIFACT_SET,
        key="15001",
    )


def test_load_game_data_preserves_canonical_material_identity() -> None:
    loaded = load_game_data(Provider())

    assert loaded.data.materials[0].identity == CanonicalId(
        kind=EntityKind.MATERIAL,
        key="104003",
    )


def test_load_game_data_rejects_provider_source_version_mismatch() -> None:
    with pytest.raises(ValueError, match="version"):
        load_game_data(MismatchedSourceProvider())


def test_load_game_data_propagates_static_dataset_validation() -> None:
    with pytest.raises(ValueError, match="duplicate character"):
        load_game_data(DuplicateCharacterProvider())


def test_load_game_data_allows_source_without_revision() -> None:
    loaded = load_game_data(NoRevisionProvider())

    assert loaded.source.revision is None
