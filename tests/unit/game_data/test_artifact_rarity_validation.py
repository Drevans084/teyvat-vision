from teyvat_vision.domain.account import (
    AccountSnapshot,
    SectionStatus,
    SnapshotSection,
)
from teyvat_vision.domain.artifact import Artifact, ArtifactSlot, StatValue
from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.domain.instance_identity import OwnedItemId
from teyvat_vision.game_data.classification import Rarity
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
    rarities: tuple[Rarity, ...],
) -> StaticGameData:
    return StaticGameData(
        version="6.8",
        characters=(),
        weapons=(),
        artifact_sets=(
            ArtifactSetDefinition(
                identity=ARTIFACT_SET_ID,
                rarities=rarities,
            ),
        ),
        materials=(),
    )


def snapshot(
    *,
    rarity: int,
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
                    slot=ArtifactSlot.FLOWER,
                    rarity=rarity,
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


def test_artifact_rarity_matching_static_set_is_valid() -> None:
    result = validate_snapshot_against_game_data(
        snapshot(rarity=5),
        game_data(
            rarities=(Rarity.FIVE_STAR,),
        ),
    )

    assert result.is_valid
    assert result.issues == ()


def test_artifact_rarity_matching_one_of_multiple_static_tiers_is_valid() -> None:
    result = validate_snapshot_against_game_data(
        snapshot(rarity=4),
        game_data(
            rarities=(
                Rarity.FOUR_STAR,
                Rarity.FIVE_STAR,
            ),
        ),
    )

    assert result.is_valid
    assert result.issues == ()


def test_artifact_rarity_outside_static_set_is_invalid() -> None:
    account = snapshot(rarity=3)

    result = validate_snapshot_against_game_data(
        account,
        game_data(
            rarities=(
                Rarity.FOUR_STAR,
                Rarity.FIVE_STAR,
            ),
        ),
    )

    assert len(result.errors) == 1

    issue = result.errors[0]

    assert issue.code == "artifact_rarity_mismatch"
    assert issue.severity is ValidationSeverity.ERROR
    assert issue.subject == account.artifacts.items[0].identity
    assert issue.field == "rarity"


def test_unknown_static_artifact_rarities_do_not_fabricate_mismatch() -> None:
    result = validate_snapshot_against_game_data(
        snapshot(rarity=5),
        game_data(
            rarities=(),
        ),
    )

    assert result.is_valid
    assert result.issues == ()
