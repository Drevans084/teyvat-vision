"""Canonical static game-data records for Teyvat Vision."""

from dataclasses import dataclass

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.game_data.classification import WeaponType
from teyvat_vision.game_data.localization import LocalizedName


def _validate_localized_names(
    names: tuple[LocalizedName, ...],
) -> None:
    locales = tuple(name.locale for name in names)

    if len(set(locales)) != len(locales):
        raise ValueError("duplicate locale in localized names")


def _validate_weapon_type(
    weapon_type: object,
    *,
    subject: str,
) -> None:
    if weapon_type is not None and not isinstance(
        weapon_type,
        WeaponType,
    ):
        raise ValueError(f"{subject} weapon type must be a canonical WeaponType")


@dataclass(frozen=True, slots=True)
class CharacterDefinition:
    """Static game definition for one canonical character."""

    identity: CanonicalId
    names: tuple[LocalizedName, ...] = ()
    weapon_type: WeaponType | None = None

    def __post_init__(self) -> None:
        if self.identity.kind is not EntityKind.CHARACTER:
            raise ValueError("character definition identity must have EntityKind.CHARACTER")

        _validate_localized_names(self.names)

        _validate_weapon_type(
            self.weapon_type,
            subject="character",
        )


@dataclass(frozen=True, slots=True)
class WeaponDefinition:
    """Static game definition for one canonical weapon."""

    identity: CanonicalId
    names: tuple[LocalizedName, ...] = ()
    weapon_type: WeaponType | None = None

    def __post_init__(self) -> None:
        if self.identity.kind is not EntityKind.WEAPON:
            raise ValueError("weapon definition identity must have EntityKind.WEAPON")

        _validate_localized_names(self.names)

        _validate_weapon_type(
            self.weapon_type,
            subject="weapon",
        )


@dataclass(frozen=True, slots=True)
class ArtifactSetDefinition:
    """Static game definition for one canonical artifact set."""

    identity: CanonicalId
    names: tuple[LocalizedName, ...] = ()

    def __post_init__(self) -> None:
        if self.identity.kind is not EntityKind.ARTIFACT_SET:
            raise ValueError("artifact set definition identity must have EntityKind.ARTIFACT_SET")

        _validate_localized_names(self.names)


@dataclass(frozen=True, slots=True)
class MaterialDefinition:
    """Static game definition for one canonical material."""

    identity: CanonicalId
    names: tuple[LocalizedName, ...] = ()

    def __post_init__(self) -> None:
        if self.identity.kind is not EntityKind.MATERIAL:
            raise ValueError("material definition identity must have EntityKind.MATERIAL")

        _validate_localized_names(self.names)
