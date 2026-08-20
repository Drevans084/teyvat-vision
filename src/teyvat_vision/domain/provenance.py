"""Provenance primitives for Teyvat Vision.

Provenance records where trusted data originated so derived account state,
training data, and validation evidence remain traceable.
"""

from dataclasses import dataclass
from enum import StrEnum


class ProvenanceKind(StrEnum):
    """Supported provenance classifications."""

    MANUAL_VERIFIED = "manual_verified"
    GAME_DATA_DERIVED = "game_data_derived"
    API_VERIFIED = "api_verified"
    SYNTHETIC_FROM_VERIFIED_ASSETS = "synthetic_from_verified_assets"


@dataclass(frozen=True, slots=True)
class Provenance:
    """Traceable origin for a trusted piece of data."""

    kind: ProvenanceKind
    source: str
    reference: str | None = None

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("source must not be blank")

        if self.source != self.source.strip():
            raise ValueError("source must not contain surrounding whitespace")

        if self.reference is not None:
            if not self.reference.strip():
                raise ValueError("reference must not be blank when provided")

            if self.reference != self.reference.strip():
                raise ValueError("reference must not contain surrounding whitespace")
