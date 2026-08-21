from teyvat_vision.domain.account import (
    AccountSnapshot,
    SectionStatus,
    SnapshotSection,
)
from teyvat_vision.domain.artifact import Artifact, ArtifactSlot, StatValue
from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.domain.instance_identity import OwnedItemId
from teyvat_vision.game_data.dataset import StaticGameData
from teyvat_vision.game_data.records import ArtifactSetDefinition
from teyvat_vision.game_data.validation import (
    ValidationSeverity,
    validate_snapshot_against_game_data,
)


ARTIFACT_SET_ID = CanonicalId(
    kind=EntityKind.ARTIFACT_SET,
    key="15001",
)


def game_data(
    *,
    slots: tuple[ArtifactSlot, ...],
) -> StaticGameData:
    return StaticGameData(
        version="6.8",
        characters=(),
        weapons=(),
        artifact_sets=(
            ArtifactSetDefinition(
                identity=ARTIFACT_SET_ID,
                slots=slots,
            ),
        ),
        materials=(),
    )


def snapshot(
    *,
    slot: ArtifactSlot,
) -> AccountSnapshot:
    return AccountSnapshot(
        characters=SnapshotSection(
            status=SectionStatus.NOT_SCANNED,
            items=(),
        ),
        weapons=SnapshotSection(
            status=SectionStatus.NOT_SCANNED,
            items=(),
        ),
        artifacts=SnapshotSection(
            status=SectionStatus.COMPLETE,
            items=(
                Artifact(
                    identity=OwnedItemId(
                        definition=ARTIFACT_SET_ID,
                        instance_key="artifact-1",
                    ),
                    slot=slot,
                    rarity=5,
                    level=20,
                    main_stat=StatValue(
                        key="hp",
                        value=4780.0,
                    ),
                    substats=(),
                    locked=False,
                ),
            ),
        ),
        materials=SnapshotSection(
            status=SectionStatus.NOT_SCANNED,
            items=(),
        ),
    )


def test_artifact_slot_matching_static_set_is_valid() -> None:
    result = validate_snapshot_against_game_data(
        snapshot(
            slot=ArtifactSlot.FLOWER,
        ),
        game_data(
            slots=(ArtifactSlot.FLOWER,),
        ),
    )

    assert result.is_valid
    assert result.issues == ()


def test_artifact_slot_matching_one_of_multiple_static_slots_is_valid() -> None:
    result = validate_snapshot_against_game_data(
        snapshot(
            slot=ArtifactSlot.GOBLET,
        ),
        game_data(
            slots=(
                ArtifactSlot.FLOWER,
                ArtifactSlot.PLUME,
                ArtifactSlot.SANDS,
                ArtifactSlot.GOBLET,
                ArtifactSlot.CIRCLET,
            ),
        ),
    )

    assert result.is_valid
    assert result.issues == ()


def test_artifact_slot_outside_static_set_is_invalid() -> None:
    account = snapshot(
        slot=ArtifactSlot.CIRCLET,
    )

    result = validate_snapshot_against_game_data(
        account,
        game_data(
            slots=(
                ArtifactSlot.FLOWER,
                ArtifactSlot.PLUME,
            ),
        ),
    )

    assert len(result.errors) == 1

    issue = result.errors[0]

    assert issue.code == "artifact_slot_mismatch"
    assert issue.severity is ValidationSeverity.ERROR
    assert issue.subject == account.artifacts.items[0].identity
    assert issue.field == "slot"


def test_unknown_static_artifact_slots_do_not_fabricate_mismatch() -> None:
    result = validate_snapshot_against_game_data(
        snapshot(
            slot=ArtifactSlot.CIRCLET,
        ),
        game_data(
            slots=(),
        ),
    )

    assert result.is_valid
    assert result.issues == ()
