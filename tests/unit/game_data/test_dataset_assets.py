import pytest

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.game_data.assets import AssetRole, GameDataAsset
from teyvat_vision.game_data.dataset import StaticGameData
from teyvat_vision.game_data.records import (
    ArtifactSetDefinition,
    CharacterDefinition,
    MaterialDefinition,
    WeaponDefinition,
)


def dataset(
    *,
    assets: tuple[GameDataAsset, ...] = (),
) -> StaticGameData:
    return StaticGameData(
        version="6.8",
        characters=(
            CharacterDefinition(
                identity=CanonicalId(
                    kind=EntityKind.CHARACTER,
                    key="10000047",
                )
            ),
        ),
        weapons=(
            WeaponDefinition(
                identity=CanonicalId(
                    kind=EntityKind.WEAPON,
                    key="11509",
                )
            ),
        ),
        artifact_sets=(
            ArtifactSetDefinition(
                identity=CanonicalId(
                    kind=EntityKind.ARTIFACT_SET,
                    key="15001",
                )
            ),
        ),
        materials=(
            MaterialDefinition(
                identity=CanonicalId(
                    kind=EntityKind.MATERIAL,
                    key="104003",
                )
            ),
        ),
        assets=assets,
    )


def test_static_game_data_preserves_assets() -> None:
    asset = GameDataAsset(
        subject=CanonicalId(
            kind=EntityKind.CHARACTER,
            key="10000047",
        ),
        role=AssetRole.CHARACTER_ICON,
        reference="UI_AvatarIcon_Kazuha",
    )

    static_data = dataset(
        assets=(asset,),
    )

    assert static_data.assets == (asset,)


def test_static_game_data_allows_multiple_assets_for_same_subject() -> None:
    subject = CanonicalId(
        kind=EntityKind.CHARACTER,
        key="10000047",
    )

    static_data = dataset(
        assets=(
            GameDataAsset(
                subject=subject,
                role=AssetRole.CHARACTER_ICON,
                reference="UI_AvatarIcon_Kazuha",
            ),
            GameDataAsset(
                subject=subject,
                role=AssetRole.CHARACTER_SIDE_ICON,
                reference="UI_AvatarIcon_Side_Kazuha",
            ),
        ),
    )

    assert len(static_data.assets) == 2


def test_static_game_data_rejects_asset_for_unknown_character() -> None:
    with pytest.raises(ValueError, match="asset"):
        dataset(
            assets=(
                GameDataAsset(
                    subject=CanonicalId(
                        kind=EntityKind.CHARACTER,
                        key="unknown-character",
                    ),
                    role=AssetRole.CHARACTER_ICON,
                    reference="unknown-character-asset",
                ),
            ),
        )


def test_static_game_data_rejects_asset_for_unknown_weapon() -> None:
    with pytest.raises(ValueError, match="asset"):
        dataset(
            assets=(
                GameDataAsset(
                    subject=CanonicalId(
                        kind=EntityKind.WEAPON,
                        key="unknown-weapon",
                    ),
                    role=AssetRole.WEAPON_ICON,
                    reference="unknown-weapon-asset",
                ),
            ),
        )


def test_static_game_data_rejects_asset_for_unknown_artifact_set() -> None:
    with pytest.raises(ValueError, match="asset"):
        dataset(
            assets=(
                GameDataAsset(
                    subject=CanonicalId(
                        kind=EntityKind.ARTIFACT_SET,
                        key="unknown-artifact-set",
                    ),
                    role=AssetRole.ARTIFACT_FLOWER,
                    reference="unknown-artifact-set-asset",
                ),
            ),
        )


def test_static_game_data_rejects_asset_for_unknown_material() -> None:
    with pytest.raises(ValueError, match="asset"):
        dataset(
            assets=(
                GameDataAsset(
                    subject=CanonicalId(
                        kind=EntityKind.MATERIAL,
                        key="unknown-material",
                    ),
                    role=AssetRole.MATERIAL_ICON,
                    reference="unknown-material-asset",
                ),
            ),
        )
