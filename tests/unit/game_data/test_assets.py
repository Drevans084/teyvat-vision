from typing import cast

import pytest

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.game_data.assets import AssetRole, GameDataAsset


def test_asset_roles_have_stable_serialized_values() -> None:
    assert tuple(role.value for role in AssetRole) == (
        "character_icon",
        "character_side_icon",
        "weapon_icon",
        "weapon_awakened_icon",
        "material_icon",
        "artifact_flower",
        "artifact_plume",
        "artifact_sands",
        "artifact_goblet",
        "artifact_circlet",
    )


def test_game_data_asset_preserves_subject_role_and_reference() -> None:
    subject = CanonicalId(
        kind=EntityKind.CHARACTER,
        key="10000047",
    )

    asset = GameDataAsset(
        subject=subject,
        role=AssetRole.CHARACTER_ICON,
        reference="UI_AvatarIcon_Kazuha",
    )

    assert asset.subject == subject
    assert asset.role is AssetRole.CHARACTER_ICON
    assert asset.reference == "UI_AvatarIcon_Kazuha"


@pytest.mark.parametrize(
    ("role", "kind"),
    [
        (
            AssetRole.CHARACTER_ICON,
            EntityKind.CHARACTER,
        ),
        (
            AssetRole.CHARACTER_SIDE_ICON,
            EntityKind.CHARACTER,
        ),
        (
            AssetRole.WEAPON_ICON,
            EntityKind.WEAPON,
        ),
        (
            AssetRole.WEAPON_AWAKENED_ICON,
            EntityKind.WEAPON,
        ),
        (
            AssetRole.MATERIAL_ICON,
            EntityKind.MATERIAL,
        ),
        (
            AssetRole.ARTIFACT_FLOWER,
            EntityKind.ARTIFACT_SET,
        ),
        (
            AssetRole.ARTIFACT_PLUME,
            EntityKind.ARTIFACT_SET,
        ),
        (
            AssetRole.ARTIFACT_SANDS,
            EntityKind.ARTIFACT_SET,
        ),
        (
            AssetRole.ARTIFACT_GOBLET,
            EntityKind.ARTIFACT_SET,
        ),
        (
            AssetRole.ARTIFACT_CIRCLET,
            EntityKind.ARTIFACT_SET,
        ),
    ],
)
def test_asset_roles_support_their_expected_subject_kind(
    role: AssetRole,
    kind: EntityKind,
) -> None:
    asset = GameDataAsset(
        subject=CanonicalId(
            kind=kind,
            key="test-subject",
        ),
        role=role,
        reference="test-reference",
    )

    assert asset.subject.kind is kind
    assert asset.role is role


@pytest.mark.parametrize(
    ("kind", "role"),
    [
        (
            EntityKind.CHARACTER,
            AssetRole.WEAPON_ICON,
        ),
        (
            EntityKind.WEAPON,
            AssetRole.MATERIAL_ICON,
        ),
        (
            EntityKind.ARTIFACT_SET,
            AssetRole.CHARACTER_ICON,
        ),
        (
            EntityKind.MATERIAL,
            AssetRole.ARTIFACT_FLOWER,
        ),
    ],
)
def test_game_data_asset_rejects_role_for_wrong_subject_kind(
    kind: EntityKind,
    role: AssetRole,
) -> None:
    with pytest.raises(ValueError, match="asset role"):
        GameDataAsset(
            subject=CanonicalId(
                kind=kind,
                key="test-subject",
            ),
            role=role,
            reference="test-reference",
        )


def test_game_data_asset_rejects_noncanonical_role() -> None:
    with pytest.raises(ValueError, match="asset role"):
        GameDataAsset(
            subject=CanonicalId(
                kind=EntityKind.CHARACTER,
                key="10000047",
            ),
            role=cast(
                AssetRole,
                "character_icon",
            ),
            reference="UI_AvatarIcon_Kazuha",
        )


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
            role=AssetRole.WEAPON_ICON,
            reference=reference,
        )


def test_game_data_asset_rejects_reference_with_surrounding_whitespace() -> None:
    with pytest.raises(ValueError, match="reference"):
        GameDataAsset(
            subject=CanonicalId(
                kind=EntityKind.WEAPON,
                key="11509",
            ),
            role=AssetRole.WEAPON_ICON,
            reference=" UI_EquipIcon_Sword_Widsith ",
        )


def test_game_data_asset_preserves_reference_case() -> None:
    asset = GameDataAsset(
        subject=CanonicalId(
            kind=EntityKind.MATERIAL,
            key="104003",
        ),
        role=AssetRole.MATERIAL_ICON,
        reference="UI_ItemIcon_104003",
    )

    assert asset.reference == "UI_ItemIcon_104003"


def test_game_data_asset_supports_character_subject() -> None:
    asset = GameDataAsset(
        subject=CanonicalId(
            kind=EntityKind.CHARACTER,
            key="10000047",
        ),
        role=AssetRole.CHARACTER_SIDE_ICON,
        reference="character-asset",
    )

    assert asset.subject.kind is EntityKind.CHARACTER


def test_game_data_asset_supports_weapon_subject() -> None:
    asset = GameDataAsset(
        subject=CanonicalId(
            kind=EntityKind.WEAPON,
            key="11509",
        ),
        role=AssetRole.WEAPON_AWAKENED_ICON,
        reference="weapon-asset",
    )

    assert asset.subject.kind is EntityKind.WEAPON


def test_game_data_asset_supports_artifact_set_subject() -> None:
    asset = GameDataAsset(
        subject=CanonicalId(
            kind=EntityKind.ARTIFACT_SET,
            key="15001",
        ),
        role=AssetRole.ARTIFACT_CIRCLET,
        reference="artifact-set-asset",
    )

    assert asset.subject.kind is EntityKind.ARTIFACT_SET


def test_game_data_asset_supports_material_subject() -> None:
    asset = GameDataAsset(
        subject=CanonicalId(
            kind=EntityKind.MATERIAL,
            key="104003",
        ),
        role=AssetRole.MATERIAL_ICON,
        reference="material-asset",
    )

    assert asset.subject.kind is EntityKind.MATERIAL
