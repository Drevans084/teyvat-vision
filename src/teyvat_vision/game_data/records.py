"""Canonical static game-data records for Teyvat Vision."""

from dataclasses import dataclass

from teyvat_vision.domain.identity import CanonicalId, EntityKind


@dataclass(frozen=True, slots=True)
class CharacterDefinition:
    """Static game definition for one canonical character."""

    identity: CanonicalId

    def __post_init__(self) -> None:
        if self.identity.kind is not EntityKind.CHARACTER:
            raise ValueError("character definition identity must have EntityKind.CHARACTER")


@dataclass(frozen=True, slots=True)
class WeaponDefinition:
    """Static game definition for one canonical weapon."""

    identity: CanonicalId

    def __post_init__(self) -> None:
        if self.identity.kind is not EntityKind.WEAPON:
            raise ValueError("weapon definition identity must have EntityKind.WEAPON")


@dataclass(frozen=True, slots=True)
class ArtifactSetDefinition:
    """Static game definition for one canonical artifact set."""

    identity: CanonicalId

    def __post_init__(self) -> None:
        if self.identity.kind is not EntityKind.ARTIFACT_SET:
            raise ValueError("artifact set definition identity must have EntityKind.ARTIFACT_SET")


@dataclass(frozen=True, slots=True)
class MaterialDefinition:
    """Static game definition for one canonical material."""

    identity: CanonicalId

    def __post_init__(self) -> None:
        if self.identity.kind is not EntityKind.MATERIAL:
            raise ValueError("material definition identity must have EntityKind.MATERIAL")
