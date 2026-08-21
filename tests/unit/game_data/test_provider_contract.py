from typing import runtime_checkable

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.game_data.assets import GameDataAsset
from teyvat_vision.game_data.provider import GameDataProvider
from teyvat_vision.game_data.records import (
    ArtifactSetDefinition,
    CharacterDefinition,
    MaterialDefinition,
    WeaponDefinition,
)
from teyvat_vision.game_data.source import GameDataSource


class CompleteProvider:
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
                reference="UI_AvatarIcon_Ayaka",
            ),
        )


class MissingSourceProvider:
    def version(self) -> str:
        return "6.8"

    def characters(self) -> tuple[CharacterDefinition, ...]:
        return ()

    def weapons(self) -> tuple[WeaponDefinition, ...]:
        return ()

    def artifact_sets(self) -> tuple[ArtifactSetDefinition, ...]:
        return ()

    def materials(self) -> tuple[MaterialDefinition, ...]:
        return ()

    def assets(self) -> tuple[GameDataAsset, ...]:
        return ()


class MissingAssetsProvider:
    def version(self) -> str:
        return "6.8"

    def source(self) -> GameDataSource:
        return GameDataSource(
            provider="test-provider",
            version="6.8",
        )

    def characters(self) -> tuple[CharacterDefinition, ...]:
        return ()

    def weapons(self) -> tuple[WeaponDefinition, ...]:
        return ()

    def artifact_sets(self) -> tuple[ArtifactSetDefinition, ...]:
        return ()

    def materials(self) -> tuple[MaterialDefinition, ...]:
        return ()


class IncompleteProvider:
    def version(self) -> str:
        return "6.8"


def test_game_data_provider_is_runtime_checkable_protocol() -> None:
    assert runtime_checkable(GameDataProvider) is GameDataProvider


def test_complete_provider_satisfies_game_data_provider_contract() -> None:
    provider = CompleteProvider()

    assert isinstance(provider, GameDataProvider)


def test_provider_without_source_does_not_satisfy_contract() -> None:
    provider = MissingSourceProvider()

    assert not isinstance(provider, GameDataProvider)


def test_provider_without_assets_does_not_satisfy_contract() -> None:
    provider = MissingAssetsProvider()

    assert not isinstance(provider, GameDataProvider)


def test_incomplete_provider_does_not_satisfy_game_data_provider_contract() -> None:
    provider = IncompleteProvider()

    assert not isinstance(provider, GameDataProvider)


def test_provider_exposes_version() -> None:
    provider: GameDataProvider = CompleteProvider()

    assert provider.version() == "6.8"


def test_provider_exposes_source_metadata() -> None:
    provider: GameDataProvider = CompleteProvider()

    source = provider.source()

    assert source.provider == "test-provider"
    assert source.version == "6.8"
    assert source.revision == "abc123"


def test_provider_exposes_character_definitions() -> None:
    provider: GameDataProvider = CompleteProvider()

    definitions = provider.characters()

    assert len(definitions) == 1
    assert definitions[0].identity.kind is EntityKind.CHARACTER


def test_provider_exposes_weapon_definitions() -> None:
    provider: GameDataProvider = CompleteProvider()

    definitions = provider.weapons()

    assert len(definitions) == 1
    assert definitions[0].identity.kind is EntityKind.WEAPON


def test_provider_exposes_artifact_set_definitions() -> None:
    provider: GameDataProvider = CompleteProvider()

    definitions = provider.artifact_sets()

    assert len(definitions) == 1
    assert definitions[0].identity.kind is EntityKind.ARTIFACT_SET


def test_provider_exposes_material_definitions() -> None:
    provider: GameDataProvider = CompleteProvider()

    definitions = provider.materials()

    assert len(definitions) == 1
    assert definitions[0].identity.kind is EntityKind.MATERIAL


def test_provider_exposes_assets() -> None:
    provider: GameDataProvider = CompleteProvider()

    assets = provider.assets()

    assert len(assets) == 1
    assert assets[0].subject == CanonicalId(
        kind=EntityKind.CHARACTER,
        key="10000002",
    )
    assert assets[0].reference == "UI_AvatarIcon_Ayaka"
