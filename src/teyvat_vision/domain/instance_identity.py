"""Owned-item identity primitives for Teyvat Vision.

Owned-item identities distinguish individual inventory instances from their
shared canonical game-definition identity.
"""

from dataclasses import dataclass

from teyvat_vision.domain.identity import CanonicalId, EntityKind


@dataclass(frozen=True, slots=True)
class OwnedItemId:
    """Identity for one specific account-owned weapon or artifact."""

    definition: CanonicalId
    instance_key: str

    def __post_init__(self) -> None:
        if self.definition.kind not in {
            EntityKind.WEAPON,
            EntityKind.ARTIFACT_SET,
        }:
            raise ValueError("owned item definition must reference a weapon or artifact set")

        if not self.instance_key.strip():
            raise ValueError("instance_key must not be empty")

        if self.instance_key != self.instance_key.strip():
            raise ValueError("instance_key must not contain surrounding whitespace")

    def __str__(self) -> str:
        return f"{self.definition}#{self.instance_key}"
