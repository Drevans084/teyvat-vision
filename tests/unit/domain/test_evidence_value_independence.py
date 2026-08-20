from typing import Any

from teyvat_vision.domain.account import AccountSnapshot, SectionStatus, SnapshotSection
from teyvat_vision.domain.artifact import Artifact, ArtifactSlot, StatValue
from teyvat_vision.domain.character import Character, TalentLevels
from teyvat_vision.domain.evidence import SnapshotEvidence
from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.domain.instance_identity import OwnedItemId
from teyvat_vision.domain.material import MaterialStack
from teyvat_vision.domain.observation import Observation, ObservationTarget
from teyvat_vision.domain.provenance import Provenance, ProvenanceKind
from teyvat_vision.domain.weapon import Weapon


def character_id() -> CanonicalId:
    return CanonicalId(
        kind=EntityKind.CHARACTER,
        key="10000002",
    )


def weapon_id() -> OwnedItemId:
    return OwnedItemId(
        definition=CanonicalId(
            kind=EntityKind.WEAPON,
            key="11509",
        ),
        instance_key="weapon-000001",
    )


def artifact_id() -> OwnedItemId:
    return OwnedItemId(
        definition=CanonicalId(
            kind=EntityKind.ARTIFACT_SET,
            key="15001",
        ),
        instance_key="artifact-000001",
    )


def material_id() -> CanonicalId:
    return CanonicalId(
        kind=EntityKind.MATERIAL,
        key="104003",
    )


def snapshot() -> AccountSnapshot:
    return AccountSnapshot(
        characters=SnapshotSection(
            status=SectionStatus.COMPLETE,
            items=(
                Character(
                    identity=character_id(),
                    level=90,
                    ascension=6,
                    constellation=0,
                    talents=TalentLevels(
                        normal=9,
                        skill=9,
                        burst=9,
                    ),
                ),
            ),
        ),
        weapons=SnapshotSection(
            status=SectionStatus.COMPLETE,
            items=(
                Weapon(
                    identity=weapon_id(),
                    level=90,
                    ascension=6,
                    refinement=1,
                    locked=True,
                ),
            ),
        ),
        artifacts=SnapshotSection(
            status=SectionStatus.COMPLETE,
            items=(
                Artifact(
                    identity=artifact_id(),
                    slot=ArtifactSlot.FLOWER,
                    rarity=5,
                    level=20,
                    main_stat=StatValue(
                        key="hp",
                        value=4780.0,
                    ),
                    substats=(
                        StatValue(
                            key="crit_rate",
                            value=3.9,
                        ),
                    ),
                    locked=True,
                ),
            ),
        ),
        materials=SnapshotSection(
            status=SectionStatus.COMPLETE,
            items=(
                MaterialStack(
                    identity=material_id(),
                    quantity=25,
                ),
            ),
        ),
    )


def provenance(source: str = "recognizer-a") -> Provenance:
    return Provenance(
        kind=ProvenanceKind.MANUAL_VERIFIED,
        source=source,
    )


def observation(
    *,
    subject: CanonicalId | OwnedItemId,
    field: str,
    value: Any,
    source: str = "recognizer-a",
) -> Observation[Any]:
    return Observation(
        target=ObservationTarget(
            subject=subject,
            field=field,
        ),
        value=value,
        provenance=provenance(source),
    )


def test_character_observation_may_disagree_with_canonical_value() -> None:
    evidence = SnapshotEvidence(
        snapshot=snapshot(),
        observations=(
            observation(
                subject=character_id(),
                field="level",
                value=80,
            ),
        ),
    )

    assert evidence.observations[0].value == 80
    assert evidence.snapshot.characters.items[0].level == 90


def test_weapon_observation_may_disagree_with_canonical_value() -> None:
    evidence = SnapshotEvidence(
        snapshot=snapshot(),
        observations=(
            observation(
                subject=weapon_id(),
                field="refinement",
                value=5,
            ),
        ),
    )

    assert evidence.observations[0].value == 5
    assert evidence.snapshot.weapons.items[0].refinement == 1


def test_artifact_observation_may_disagree_with_canonical_value() -> None:
    evidence = SnapshotEvidence(
        snapshot=snapshot(),
        observations=(
            observation(
                subject=artifact_id(),
                field="level",
                value=16,
            ),
        ),
    )

    assert evidence.observations[0].value == 16
    assert evidence.snapshot.artifacts.items[0].level == 20


def test_material_observation_may_disagree_with_canonical_value() -> None:
    evidence = SnapshotEvidence(
        snapshot=snapshot(),
        observations=(
            observation(
                subject=material_id(),
                field="quantity",
                value=20,
            ),
        ),
    )

    assert evidence.observations[0].value == 20
    assert evidence.snapshot.materials.items[0].quantity == 25


def test_artifact_substat_observation_may_disagree_with_canonical_value() -> None:
    evidence = SnapshotEvidence(
        snapshot=snapshot(),
        observations=(
            observation(
                subject=artifact_id(),
                field="substats.crit_rate",
                value=3.5,
            ),
        ),
    )

    assert evidence.observations[0].value == 3.5
    assert evidence.snapshot.artifacts.items[0].substats[0].value == 3.9


def test_matching_and_conflicting_observations_can_support_same_target() -> None:
    target = ObservationTarget(
        subject=character_id(),
        field="level",
    )

    matching = Observation(
        target=target,
        value=90,
        provenance=provenance("recognizer-a"),
    )
    conflicting = Observation(
        target=target,
        value=80,
        provenance=provenance("recognizer-b"),
    )

    evidence = SnapshotEvidence(
        snapshot=snapshot(),
        observations=(
            matching,
            conflicting,
        ),
    )

    assert evidence.observations == (
        matching,
        conflicting,
    )


def test_conflicting_evidence_does_not_mutate_canonical_snapshot() -> None:
    account_snapshot = snapshot()

    SnapshotEvidence(
        snapshot=account_snapshot,
        observations=(
            observation(
                subject=character_id(),
                field="level",
                value=80,
            ),
            observation(
                subject=material_id(),
                field="quantity",
                value=999,
            ),
        ),
    )

    assert account_snapshot.characters.items[0].level == 90
    assert account_snapshot.materials.items[0].quantity == 25
