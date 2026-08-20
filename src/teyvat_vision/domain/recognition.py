"""Recognition result primitives.

Recognition failures and uncertainty are represented explicitly so they cannot
silently collapse into valid-looking empty, zero, or default values.
"""

from dataclasses import dataclass
from math import isfinite


def _validate_confidence(confidence: float) -> None:
    """Validate that a confidence score is finite and within [0.0, 1.0]."""
    if not isfinite(confidence) or not 0.0 <= confidence <= 1.0:
        raise ValueError("confidence must be a finite value between 0.0 and 1.0")


def _validate_reason(reason: str) -> None:
    """Validate that a diagnostic reason contains meaningful text."""
    if not reason.strip():
        raise ValueError("reason must not be empty")


@dataclass(frozen=True, slots=True)
class Candidate[T]:
    """One plausible recognition candidate."""

    value: T
    confidence: float

    def __post_init__(self) -> None:
        _validate_confidence(self.confidence)


@dataclass(frozen=True, slots=True)
class Resolved[T]:
    """A recognition result accepted as a single resolved value."""

    value: T
    confidence: float

    def __post_init__(self) -> None:
        _validate_confidence(self.confidence)


@dataclass(frozen=True, slots=True)
class Ambiguous[T]:
    """A recognition result with multiple plausible candidates."""

    candidates: tuple[Candidate[T], ...]
    reason: str

    def __post_init__(self) -> None:
        if len(self.candidates) < 2:
            raise ValueError("ambiguous recognition requires at least two candidates")

        _validate_reason(self.reason)


@dataclass(frozen=True, slots=True)
class Unresolved:
    """Recognition could not determine a trustworthy value."""

    reason: str

    def __post_init__(self) -> None:
        _validate_reason(self.reason)


@dataclass(frozen=True, slots=True)
class Failed:
    """Recognition could not complete because an operation failed."""

    reason: str
    error_code: str | None = None

    def __post_init__(self) -> None:
        _validate_reason(self.reason)

        if self.error_code is not None and not self.error_code.strip():
            raise ValueError("error_code must not be empty when provided")


type RecognitionResult[T] = Resolved[T] | Ambiguous[T] | Unresolved | Failed
