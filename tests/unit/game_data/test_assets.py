import pytest

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.game_data.assets import GameDataAsset


def test_game_data_asset_preserves_subject_and_reference() -> None:
    subject = CanonicalId(
        kind=EntityKind.CHARACTER,
        key="10000047",
    )

    asset = GameDataAsset(
        subject=subject,
        reference="UI_AvatarIcon_Kazuha",
    )

    assert asset.subject == subject
    assert asset.reference == "UI_AvatarIcon_Kazuha"


@pytest.mark.parametrize(
    "reference",
    [
        "",
        "   ",
    ],
)
def test_game_data_asset_rejects_blank_reference(reference: str) -> None:
    with pytest.raises(ValueError, match="reference"):
        GameDataAsset(
            subject=CanonicalId(
                kind=EntityKind.WEAPON,
                key="11509",
            ),
            reference=reference,
        )


def test_game_data_asset_rejects_reference_with_surrounding_whitespace() -> None:
    with pytest.raises(ValueError, match="reference"):
        GameDataAsset(
            subject=CanonicalId(
                kind=EntityKind.WEAPON,
                key="11509",
            ),
            reference=" UI_EquipIcon_Sword_Widsith ",
        )


def test_game_data_asset_preserves_reference_case() -> None:
    asset = GameDataAsset(
        subject=CanonicalId(
            kind=EntityKind.MATERIAL,
            key="104003",
        ),
        reference="UI_ItemIcon_104003",
    )

    assert asset.reference == "UI_ItemIcon_104003"


def test_game_data_asset_supports_character_subject() -> None:
    asset = GameDataAsset(
        subject=CanonicalId(
            kind=EntityKind.CHARACTER,
            key="10000047",
        ),
        reference="character-asset",
    )

    assert asset.subject.kind is EntityKind.CHARACTER


def test_game_data_asset_supports_weapon_subject() -> None:
    asset = GameDataAsset(
        subject=CanonicalId(
            kind=EntityKind.WEAPON,
            key="11509",
        ),
        reference="weapon-asset",
    )

    assert asset.subject.kind is EntityKind.WEAPON


def test_game_data_asset_supports_artifact_set_subject() -> None:
    asset = GameDataAsset(
        subject=CanonicalId(
            kind=EntityKind.ARTIFACT_SET,
            key="15001",
        ),
        reference="artifact-set-asset",
    )

    assert asset.subject.kind is EntityKind.ARTIFACT_SET


def test_game_data_asset_supports_material_subject() -> None:
    asset = GameDataAsset(
        subject=CanonicalId(
            kind=EntityKind.MATERIAL,
            key="104003",
        ),
        reference="material-asset",
    )

    assert asset.subject.kind is EntityKind.MATERIAL
