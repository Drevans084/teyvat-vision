"""Observation and evidence primitives for Teyvat Vision.

Observations preserve the evidence supporting canonical account state without
embedding provenance or recognition metadata directly into domain entities.
"""

from dataclasses import dataclass
from datetime import datetime
from math import isfinite

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.domain.instance_identity import OwnedItemId
from teyvat_vision.domain.provenance import Provenance


type ObservationSubject = CanonicalId | OwnedItemId


@dataclass(frozen=True, slots=True)
class ObservationTarget:
    """Address one observable property of a canonical account subject."""

    subject: ObservationSubject
    field: str

    def __post_init__(self) -> None:
        if isinstance(self.subject, CanonicalId) and self.subject.kind in {
            EntityKind.WEAPON,
            EntityKind.ARTIFACT_SET,
        }:
            raise ValueError(
                "weapon and artifact observations must reference an owned item identity"
            )

        if not self.field.strip():
            raise ValueError("field must not be blank")

        if self.field != self.field.strip():
            raise ValueError("field must not contain surrounding whitespace")

    def __str__(self) -> str:
        return f"{self.subject}.{self.field}"


@dataclass(frozen=True, slots=True)
class Observation[T]:
    """One piece of evidence supporting an observed or derived field value."""

    target: ObservationTarget
    value: T
    provenance: Provenance
    confidence: float | None = None
    capture_ref: str | None = None
    diagnostic_ref: str | None = None
    recognizer: str | None = None
    observed_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.confidence is not None:
            if not isfinite(self.confidence) or not 0.0 <= self.confidence <= 1.0:
                raise ValueError("confidence must be a finite value between 0.0 and 1.0")

        self._validate_optional_text(
            "capture_ref",
            self.capture_ref,
        )
        self._validate_optional_text(
            "diagnostic_ref",
            self.diagnostic_ref,
        )
        self._validate_optional_text(
            "recognizer",
            self.recognizer,
        )

        if self.observed_at is not None and (
            self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None
        ):
            raise ValueError("observed_at must be timezone-aware")

    @staticmethod
    def _validate_optional_text(
        field_name: str,
        value: str | None,
    ) -> None:
        if value is None:
            return

        if not value.strip():
            raise ValueError(f"{field_name} must not be blank")

        if value != value.strip():
            raise ValueError(f"{field_name} must not contain surrounding whitespace")
