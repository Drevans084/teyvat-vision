import pytest

from teyvat_vision.domain.provenance import Provenance, ProvenanceKind


def test_manual_verified_provenance_preserves_source() -> None:
    provenance = Provenance(
        kind=ProvenanceKind.MANUAL_VERIFIED,
        source="artifact-capture-set-001",
    )

    assert provenance.kind is ProvenanceKind.MANUAL_VERIFIED
    assert provenance.source == "artifact-capture-set-001"
    assert provenance.reference is None


def test_game_data_provenance_can_record_upstream_reference() -> None:
    provenance = Provenance(
        kind=ProvenanceKind.GAME_DATA_DERIVED,
        source="AnimeGameData",
        reference="26df1d",
    )

    assert provenance.source == "AnimeGameData"
    assert provenance.reference == "26df1d"


def test_api_verified_provenance_can_record_provider_reference() -> None:
    provenance = Provenance(
        kind=ProvenanceKind.API_VERIFIED,
        source="Enka.Network",
        reference="response-cache-0001",
    )

    assert provenance.kind is ProvenanceKind.API_VERIFIED
    assert provenance.reference == "response-cache-0001"


def test_synthetic_provenance_is_explicit() -> None:
    provenance = Provenance(
        kind=ProvenanceKind.SYNTHETIC_FROM_VERIFIED_ASSETS,
        source="verified-artifact-icons-v1",
    )

    assert provenance.kind is ProvenanceKind.SYNTHETIC_FROM_VERIFIED_ASSETS


@pytest.mark.parametrize(
    "source",
    [
        "",
        "   ",
        "\t",
        "\n",
    ],
)
def test_provenance_rejects_blank_source(source: str) -> None:
    with pytest.raises(ValueError, match="source"):
        Provenance(
            kind=ProvenanceKind.MANUAL_VERIFIED,
            source=source,
        )


@pytest.mark.parametrize(
    "source",
    [
        " source",
        "source ",
        " source ",
    ],
)
def test_provenance_rejects_surrounding_whitespace_in_source(source: str) -> None:
    with pytest.raises(ValueError, match="source"):
        Provenance(
            kind=ProvenanceKind.MANUAL_VERIFIED,
            source=source,
        )


@pytest.mark.parametrize(
    "reference",
    [
        "",
        "   ",
        "\t",
        "\n",
    ],
)
def test_provenance_rejects_blank_reference_when_provided(reference: str) -> None:
    with pytest.raises(ValueError, match="reference"):
        Provenance(
            kind=ProvenanceKind.GAME_DATA_DERIVED,
            source="AnimeGameData",
            reference=reference,
        )


def test_provenance_rejects_surrounding_whitespace_in_reference() -> None:
    with pytest.raises(ValueError, match="reference"):
        Provenance(
            kind=ProvenanceKind.GAME_DATA_DERIVED,
            source="AnimeGameData",
            reference=" 26df1d ",
        )


def test_provenance_preserves_case_exactly() -> None:
    upper = Provenance(
        kind=ProvenanceKind.API_VERIFIED,
        source="ProviderAPI",
    )
    lower = Provenance(
        kind=ProvenanceKind.API_VERIFIED,
        source="providerapi",
    )

    assert upper.source == "ProviderAPI"
    assert lower.source == "providerapi"
    assert upper != lower
