import pytest

from teyvat_vision.domain.artifact import ArtifactSlot
from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.game_data.records import ArtifactSetDefinition

ARTIFACT_SET_ID = CanonicalId(
    kind=EntityKind.ARTIFACT_SET,
    key="15001",
)


def test_artifact_set_defaults_to_unknown_slots() -> None:
    definition = ArtifactSetDefinition(
        identity=ARTIFACT_SET_ID,
    )

    assert definition.slots == ()


def test_artifact_set_preserves_single_slot() -> None:
    definition = ArtifactSetDefinition(
        identity=ARTIFACT_SET_ID,
        slots=(ArtifactSlot.CIRCLET,),
    )

    assert definition.slots == (ArtifactSlot.CIRCLET,)


def test_artifact_set_preserves_multiple_slots() -> None:
    definition = ArtifactSetDefinition(
        identity=ARTIFACT_SET_ID,
        slots=(
            ArtifactSlot.FLOWER,
            ArtifactSlot.PLUME,
            ArtifactSlot.SANDS,
            ArtifactSlot.GOBLET,
            ArtifactSlot.CIRCLET,
        ),
    )

    assert definition.slots == (
        ArtifactSlot.FLOWER,
        ArtifactSlot.PLUME,
        ArtifactSlot.SANDS,
        ArtifactSlot.GOBLET,
        ArtifactSlot.CIRCLET,
    )


def test_artifact_set_rejects_duplicate_slot() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        ArtifactSetDefinition(
            identity=ARTIFACT_SET_ID,
            slots=(
                ArtifactSlot.FLOWER,
                ArtifactSlot.FLOWER,
            ),
        )


def test_artifact_set_rejects_raw_string_slot() -> None:
    with pytest.raises(ValueError, match="canonical ArtifactSlot"):
        ArtifactSetDefinition(
            identity=ARTIFACT_SET_ID,
            slots=("flower",),  # type: ignore[arg-type]
        )
