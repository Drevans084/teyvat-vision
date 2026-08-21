from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.game_data.assets import GameDataAsset
from teyvat_vision.game_data.loader import load_game_data
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
                    key="10000047",
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
                    key="10000047",
                ),
                reference="UI_AvatarIcon_Kazuha",
            ),
        )


class UnknownAssetProvider(Provider):
    def assets(self) -> tuple[GameDataAsset, ...]:
        return (
            GameDataAsset(
                subject=CanonicalId(
                    kind=EntityKind.CHARACTER,
                    key="unknown-character",
                ),
                reference="unknown-character-asset",
            ),
        )


def test_load_game_data_preserves_provider_assets() -> None:
    loaded = load_game_data(Provider())

    assert loaded.data.assets == (
        GameDataAsset(
            subject=CanonicalId(
                kind=EntityKind.CHARACTER,
                key="10000047",
            ),
            reference="UI_AvatarIcon_Kazuha",
        ),
    )


def test_load_game_data_validates_provider_asset_subjects() -> None:
    try:
        load_game_data(UnknownAssetProvider())
    except ValueError as error:
        assert "asset" in str(error)
    else:
        raise AssertionError("expected invalid asset subject to be rejected")
