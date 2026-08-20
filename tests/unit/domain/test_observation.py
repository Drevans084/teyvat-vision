from datetime import UTC, datetime
from typing import Literal

import pytest

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.domain.observation import Observation, ObservationTarget
from teyvat_vision.domain.provenance import Provenance, ProvenanceKind

type OptionalTextField = Literal[
    "capture_ref",
    "diagnostic_ref",
    "recognizer",
]


def character_target(field: str = "level") -> ObservationTarget:
    return ObservationTarget(
        subject=CanonicalId(
            kind=EntityKind.CHARACTER,
            key="10000002",
        ),
        field=field,
    )


def provenance() -> Provenance:
    return Provenance(
        kind=ProvenanceKind.MANUAL_VERIFIED,
        source="verified-fixture",
        reference="fixture-001",
    )


def observation_with_optional_text(
    field_name: OptionalTextField,
    value: str,
) -> Observation[int]:
    if field_name == "capture_ref":
        return Observation(
            target=character_target(),
            value=90,
            provenance=provenance(),
            capture_ref=value,
        )

    if field_name == "diagnostic_ref":
        return Observation(
            target=character_target(),
            value=90,
            provenance=provenance(),
            diagnostic_ref=value,
        )

    return Observation(
        target=character_target(),
        value=90,
        provenance=provenance(),
        recognizer=value,
    )


def test_observation_preserves_core_evidence() -> None:
    target = character_target()
    source = provenance()

    observation = Observation(
        target=target,
        value=90,
        provenance=source,
    )

    assert observation.target == target
    assert observation.value == 90
    assert observation.provenance == source
    assert observation.confidence is None


def test_observation_can_preserve_recognition_confidence() -> None:
    observation = Observation(
        target=character_target(),
        value=90,
        provenance=provenance(),
        confidence=0.987,
    )

    assert observation.confidence == 0.987


@pytest.mark.parametrize(
    "confidence",
    [
        -0.01,
        1.01,
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_observation_rejects_invalid_confidence(confidence: float) -> None:
    with pytest.raises(ValueError, match="confidence"):
        Observation(
            target=character_target(),
            value=90,
            provenance=provenance(),
            confidence=confidence,
        )


def test_observation_can_reference_capture_evidence() -> None:
    observation = Observation(
        target=character_target(),
        value=90,
        provenance=provenance(),
        capture_ref="capture/artifact-detail-0001.png",
    )

    assert observation.capture_ref == "capture/artifact-detail-0001.png"


def test_observation_can_reference_diagnostic_evidence() -> None:
    observation = Observation(
        target=character_target(),
        value=90,
        provenance=provenance(),
        diagnostic_ref="diagnostics/run-0001/level.json",
    )

    assert observation.diagnostic_ref == "diagnostics/run-0001/level.json"


def test_observation_can_record_recognizer_identity() -> None:
    observation = Observation(
        target=character_target(),
        value=90,
        provenance=provenance(),
        recognizer="character-level-v1",
    )

    assert observation.recognizer == "character-level-v1"


@pytest.mark.parametrize(
    "field_name",
    [
        "capture_ref",
        "diagnostic_ref",
        "recognizer",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
        "\t",
        "\n",
    ],
)
def test_observation_rejects_blank_optional_text(
    field_name: OptionalTextField,
    value: str,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        observation_with_optional_text(
            field_name,
            value,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "capture_ref",
        "diagnostic_ref",
        "recognizer",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        " value",
        "value ",
        " value ",
    ],
)
def test_observation_rejects_surrounding_whitespace_in_optional_text(
    field_name: OptionalTextField,
    value: str,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        observation_with_optional_text(
            field_name,
            value,
        )


def test_observation_can_record_timezone_aware_timestamp() -> None:
    observed_at = datetime(
        2026,
        8,
        19,
        23,
        30,
        tzinfo=UTC,
    )

    observation = Observation(
        target=character_target(),
        value=90,
        provenance=provenance(),
        observed_at=observed_at,
    )

    assert observation.observed_at == observed_at


def test_observation_rejects_naive_timestamp() -> None:
    observed_at = datetime(
        2026,
        8,
        19,
        23,
        30,
    )

    with pytest.raises(ValueError, match="timezone"):
        Observation(
            target=character_target(),
            value=90,
            provenance=provenance(),
            observed_at=observed_at,
        )


def test_multiple_observations_can_support_same_target() -> None:
    target = character_target()

    first = Observation(
        target=target,
        value=90,
        provenance=Provenance(
            kind=ProvenanceKind.MANUAL_VERIFIED,
            source="verified-fixture",
        ),
    )
    second = Observation(
        target=target,
        value=90,
        provenance=Provenance(
            kind=ProvenanceKind.API_VERIFIED,
            source="validation-provider",
        ),
    )

    assert first.target == second.target
    assert first.provenance != second.provenance


def test_observation_value_is_generic() -> None:
    observation = Observation(
        target=character_target("custom_name"),
        value="Traveler",
        provenance=provenance(),
    )

    assert observation.value == "Traveler"