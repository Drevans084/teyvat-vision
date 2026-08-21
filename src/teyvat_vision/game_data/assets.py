"""Provider-independent static game-data asset references."""

from dataclasses import dataclass
from enum import StrEnum

from teyvat_vision.domain.identity import CanonicalId, EntityKind


class AssetRole(StrEnum):
    """Semantic roles for symbolic static game-data assets."""

    CHARACTER_ICON = "character_icon"
    CHARACTER_SIDE_ICON = "character_side_icon"
    WEAPON_ICON = "weapon_icon"
    WEAPON_AWAKENED_ICON = "weapon_awakened_icon"
    MATERIAL_ICON = "material_icon"
    ARTIFACT_FLOWER = "artifact_flower"
    ARTIFACT_PLUME = "artifact_plume"
    ARTIFACT_SANDS = "artifact_sands"
    ARTIFACT_GOBLET = "artifact_goblet"
    ARTIFACT_CIRCLET = "artifact_circlet"


_ASSET_ROLE_SUBJECT_KINDS = {
    AssetRole.CHARACTER_ICON: EntityKind.CHARACTER,
    AssetRole.CHARACTER_SIDE_ICON: EntityKind.CHARACTER,
    AssetRole.WEAPON_ICON: EntityKind.WEAPON,
    AssetRole.WEAPON_AWAKENED_ICON: EntityKind.WEAPON,
    AssetRole.MATERIAL_ICON: EntityKind.MATERIAL,
    AssetRole.ARTIFACT_FLOWER: EntityKind.ARTIFACT_SET,
    AssetRole.ARTIFACT_PLUME: EntityKind.ARTIFACT_SET,
    AssetRole.ARTIFACT_SANDS: EntityKind.ARTIFACT_SET,
    AssetRole.ARTIFACT_GOBLET: EntityKind.ARTIFACT_SET,
    AssetRole.ARTIFACT_CIRCLET: EntityKind.ARTIFACT_SET,
}


def _validate_asset_role(role: object) -> AssetRole:
    if not isinstance(role, AssetRole):
        raise ValueError("asset role must be a canonical AssetRole")

    return role


@dataclass(frozen=True, slots=True)
class GameDataAsset:
    """Associates one canonical entity with a typed symbolic asset reference."""

    subject: CanonicalId
    role: AssetRole
    reference: str

    def __post_init__(self) -> None:
        role = _validate_asset_role(self.role)
        expected_kind = _ASSET_ROLE_SUBJECT_KINDS[role]

        if self.subject.kind is not expected_kind:
            raise ValueError(
                f"asset role {role.value!r} requires subject kind {expected_kind.value!r}"
            )

        if not self.reference.strip():
            raise ValueError("reference must not be blank")

        if self.reference != self.reference.strip():
            raise ValueError("reference must not contain surrounding whitespace")
