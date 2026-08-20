import pytest

from teyvat_vision.domain.recognition import (
    Ambiguous,
    Candidate,
    Failed,
    Resolved,
    Unresolved,
)


def test_resolved_requires_confidence_in_unit_interval() -> None:
    result = Resolved(value="mistsplitter_reforged", confidence=0.98)

    assert result.value == "mistsplitter_reforged"
    assert result.confidence == 0.98


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_resolved_rejects_invalid_confidence(confidence: float) -> None:
    with pytest.raises(ValueError, match="confidence"):
        Resolved(value="mistsplitter_reforged", confidence=confidence)


def test_candidate_requires_confidence_in_unit_interval() -> None:
    candidate = Candidate(value="ayaka", confidence=0.75)

    assert candidate.value == "ayaka"
    assert candidate.confidence == 0.75


@pytest.mark.parametrize("confidence", [-1.0, 1.5])
def test_candidate_rejects_invalid_confidence(confidence: float) -> None:
    with pytest.raises(ValueError, match="confidence"):
        Candidate(value="ayaka", confidence=confidence)


def test_ambiguous_requires_at_least_two_candidates() -> None:
    with pytest.raises(ValueError, match="at least two"):
        Ambiguous(
            candidates=(Candidate(value="ayaka", confidence=0.75),),
            reason="Multiple visually plausible identities.",
        )


def test_ambiguous_preserves_candidates_and_reason() -> None:
    candidates = (
        Candidate(value="ayaka", confidence=0.75),
        Candidate(value="ayato", confidence=0.71),
    )

    result = Ambiguous(
        candidates=candidates,
        reason="Multiple visually plausible identities.",
    )

    assert result.candidates == candidates
    assert result.reason == "Multiple visually plausible identities."


def test_unresolved_requires_reason() -> None:
    with pytest.raises(ValueError, match="reason"):
        Unresolved(reason="   ")


def test_failed_requires_reason() -> None:
    with pytest.raises(ValueError, match="reason"):
        Failed(reason="")


def test_failed_can_record_error_code() -> None:
    result = Failed(
        reason="ROI extraction failed.",
        error_code="roi_extraction_failed",
    )

    assert result.reason == "ROI extraction failed."
    assert result.error_code == "roi_extraction_failed"
