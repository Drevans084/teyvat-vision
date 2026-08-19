"""Material domain model for Teyvat Vision.

Material stacks represent known account-owned quantities. Unknown quantities
must remain unresolved upstream rather than being represented as zero.
"""

from dataclasses import dataclass

from teyvat_vision.domain.identity import CanonicalId, EntityKind


@dataclass(frozen=True, slots=True)
class MaterialStack:
    """Canonical state for one owned material stack."""

    identity: CanonicalId
    quantity: int

    def __post_init__(self) -> None:
        if self.identity.kind is not EntityKind.MATERIAL:
            raise ValueError("material identity must have EntityKind.MATERIAL")

        if type(self.quantity) is not int:
            raise ValueError("quantity must be an integer")

        if self.quantity <= 0:
            raise ValueError("quantity must be greater than zero")
