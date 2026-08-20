from typing import Any

import pytest

from teyvat_vision.domain.account import AccountSnapshot, SectionStatus, SnapshotSection
from teyvat_vision.domain.artifact import Artifact, ArtifactSlot, StatValue
from teyvat_vision.domain.character import Character, TalentLevels
from teyvat_vision.domain.evidence import SnapshotEvidence
from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.domain.instance_identity import OwnedItemId
from teyvat_vision.domain.material import MaterialStack
from teyvat_vision.domain.observation import (
    Observation,
    ObservationSubject,
    ObservationTarget,
)
from teyvat_vision.domain.provenance import Provenance, ProvenanceKind
from teyvat_vision.domain.weapon import Weapon


def character_id(key: str = "10000002") -> CanonicalId:
    return CanonicalId(
        kind=EntityKind.CHARACTER,
        key=key,
    )


def weapon_definition(key: str = "11509") -> CanonicalId:
    return CanonicalId(
        kind=EntityKind.WEAPON,
        key=key,
    )


def weapon_id(
    key: str = "11509",
    *,
    instance_key: str = "weapon-000001",
) -> OwnedItemId:
    return OwnedItemId(
        definition=weapon_definition(key),
        instance_key=instance_key,
    )


def artifact_set_definition(key: str = "15001") -> CanonicalId:
    return CanonicalId(
        kind=EntityKind.ARTIFACT_SET,
        key=key,
    )


def artifact_id(
    key: str = "15001",
    *,
    instance_key: str = "artifact-000001",
) -> OwnedItemId:
    return OwnedItemId(
        definition=artifact_set_definition(key),
        instance_key=instance_key,
    )


def material_id(key: str = "104003") -> CanonicalId:
    return CanonicalId(
        kind=EntityKind.MATERIAL,
        key=key,
    )


def character(key: str = "10000002") -> Character:
    return Character(
        identity=character_id(key),
        level=90,
        ascension=6,
        constellation=0,
        talents=TalentLevels(
            normal=9,
            skill=9,
            burst=9,
        ),
    )


def weapon(
    key: str = "11509",
    *,
    instance_key: str = "weapon-000001",
) -> Weapon:
    return Weapon(
        identity=weapon_id(
            key,
            instance_key=instance_key,
        ),
        level=90,
        ascension=6,
        refinement=1,
        locked=True,
    )


def artifact(
    key: str = "15001",
    *,
    instance_key: str = "artifact-000001",
) -> Artifact:
    return Artifact(
        identity=artifact_id(
            key,
            instance_key=instance_key,
        ),
        slot=ArtifactSlot.FLOWER,
        rarity=5,
        level=20,
        main_stat=StatValue(
            key="hp",
            value=4780.0,
        ),
        substats=(),
        locked=True,
    )


def material(
    key: str = "104003",
    *,
    quantity: int = 10,
) -> MaterialStack:
    return MaterialStack(
        identity=material_id(key),
        quantity=quantity,
    )


def snapshot(
    *,
    characters: tuple[Character, ...] | None = None,
    weapons: tuple[Weapon, ...] = (),
    artifacts: tuple[Artifact, ...] = (),
    materials: tuple[MaterialStack, ...] = (),
    character_status: SectionStatus = SectionStatus.COMPLETE,
    weapon_status: SectionStatus = SectionStatus.COMPLETE,
    artifact_status: SectionStatus = SectionStatus.COMPLETE,
    material_status: SectionStatus = SectionStatus.COMPLETE,
) -> AccountSnapshot:
    if characters is None:
        characters = (character(),)

    return AccountSnapshot(
        characters=SnapshotSection(
            status=character_status,
            items=characters,
        ),
        weapons=SnapshotSection(
            status=weapon_status,
            items=weapons,
        ),
        artifacts=SnapshotSection(
            status=artifact_status,
            items=artifacts,
        ),
        materials=SnapshotSection(
            status=material_status,
            items=materials,
        ),
    )


def observation(
    subject: ObservationSubject | None = None,
    *,
    field: str = "level",
    value: Any = 90,
) -> Observation[Any]:
    return Observation(
        target=ObservationTarget(
            subject=subject or character_id(),
            field=field,
        ),
        value=value,
        provenance=Provenance(
            kind=ProvenanceKind.MANUAL_VERIFIED,
            source="verified-fixture",
        ),
    )


def test_snapshot_evidence_preserves_snapshot_and_observations() -> None:
    account_snapshot = snapshot()
    observations = (observation(),)

    snapshot_evidence = SnapshotEvidence(
        snapshot=account_snapshot,
        observations=observations,
    )

    assert snapshot_evidence.snapshot == account_snapshot
    assert snapshot_evidence.observations == observations


def test_snapshot_evidence_allows_empty_observation_collection() -> None:
    account_snapshot = snapshot()

    snapshot_evidence = SnapshotEvidence(
        snapshot=account_snapshot,
        observations=(),
    )

    assert snapshot_evidence.observations == ()


def test_snapshot_evidence_accepts_observation_for_present_character() -> None:
    account_snapshot = snapshot(
        characters=(character("10000002"),),
    )

    snapshot_evidence = SnapshotEvidence(
        snapshot=account_snapshot,
        observations=(
            observation(
                subject=character_id("10000002"),
            ),
        ),
    )

    assert snapshot_evidence.observations[0].target.subject == character_id("10000002")


def test_snapshot_evidence_rejects_observation_for_absent_character() -> None:
    with pytest.raises(ValueError, match="observation subject"):
        SnapshotEvidence(
            snapshot=snapshot(
                characters=(character("10000002"),),
            ),
            observations=(
                observation(
                    subject=character_id("10000099"),
                ),
            ),
        )


def test_snapshot_evidence_accepts_present_character_in_partial_section() -> None:
    account_snapshot = snapshot(
        characters=(character("10000002"),),
        character_status=SectionStatus.PARTIAL,
    )

    snapshot_evidence = SnapshotEvidence(
        snapshot=account_snapshot,
        observations=(
            observation(
                subject=character_id("10000002"),
            ),
        ),
    )

    assert snapshot_evidence.observations[0].target.subject == character_id("10000002")


def test_snapshot_evidence_rejects_absent_character_from_partial_section() -> None:
    with pytest.raises(ValueError, match="observation subject"):
        SnapshotEvidence(
            snapshot=snapshot(
                characters=(character("10000002"),),
                character_status=SectionStatus.PARTIAL,
            ),
            observations=(
                observation(
                    subject=character_id("10000099"),
                ),
            ),
        )


def test_snapshot_evidence_accepts_observation_for_present_material() -> None:
    account_snapshot = snapshot(
        materials=(material("104003"),),
    )

    snapshot_evidence = SnapshotEvidence(
        snapshot=account_snapshot,
        observations=(
            observation(
                subject=material_id("104003"),
                field="quantity",
                value=10,
            ),
        ),
    )

    assert snapshot_evidence.observations[0].target.subject == material_id("104003")


def test_snapshot_evidence_rejects_observation_for_absent_material() -> None:
    with pytest.raises(ValueError, match="observation subject"):
        SnapshotEvidence(
            snapshot=snapshot(
                materials=(material("104003"),),
            ),
            observations=(
                observation(
                    subject=material_id("104004"),
                    field="quantity",
                    value=25,
                ),
            ),
        )


def test_snapshot_evidence_accepts_observation_for_present_weapon_instance() -> None:
    owned_weapon = weapon(
        "11509",
        instance_key="weapon-000001",
    )

    snapshot_evidence = SnapshotEvidence(
        snapshot=snapshot(
            weapons=(owned_weapon,),
        ),
        observations=(
            observation(
                subject=owned_weapon.identity,
                field="refinement",
                value=1,
            ),
        ),
    )

    assert snapshot_evidence.observations[0].target.subject == owned_weapon.identity


def test_snapshot_evidence_rejects_absent_weapon_instance_with_same_definition() -> None:
    present_weapon = weapon(
        "11509",
        instance_key="weapon-000001",
    )
    absent_weapon_id = weapon_id(
        "11509",
        instance_key="weapon-000002",
    )

    with pytest.raises(ValueError, match="observation subject"):
        SnapshotEvidence(
            snapshot=snapshot(
                weapons=(present_weapon,),
            ),
            observations=(
                observation(
                    subject=absent_weapon_id,
                    field="refinement",
                    value=1,
                ),
            ),
        )


def test_snapshot_evidence_accepts_observation_for_present_artifact_instance() -> None:
    owned_artifact = artifact(
        "15001",
        instance_key="artifact-000001",
    )

    snapshot_evidence = SnapshotEvidence(
        snapshot=snapshot(
            artifacts=(owned_artifact,),
        ),
        observations=(
            observation(
                subject=owned_artifact.identity,
                field="level",
                value=20,
            ),
        ),
    )

    assert snapshot_evidence.observations[0].target.subject == owned_artifact.identity


def test_snapshot_evidence_rejects_absent_artifact_instance_with_same_definition() -> None:
    present_artifact = artifact(
        "15001",
        instance_key="artifact-000001",
    )
    absent_artifact_id = artifact_id(
        "15001",
        instance_key="artifact-000002",
    )

    with pytest.raises(ValueError, match="observation subject"):
        SnapshotEvidence(
            snapshot=snapshot(
                artifacts=(present_artifact,),
            ),
            observations=(
                observation(
                    subject=absent_artifact_id,
                    field="level",
                    value=20,
                ),
            ),
        )


def test_snapshot_evidence_accepts_observations_for_all_represented_subject_kinds() -> None:
    owned_character = character("10000002")
    owned_weapon = weapon(
        "11509",
        instance_key="weapon-000001",
    )
    owned_artifact = artifact(
        "15001",
        instance_key="artifact-000001",
    )
    owned_material = material("104003")

    observations = (
        observation(
            subject=owned_character.identity,
            field="level",
            value=90,
        ),
        observation(
            subject=owned_weapon.identity,
            field="refinement",
            value=1,
        ),
        observation(
            subject=owned_artifact.identity,
            field="level",
            value=20,
        ),
        observation(
            subject=owned_material.identity,
            field="quantity",
            value=10,
        ),
    )

    snapshot_evidence = SnapshotEvidence(
        snapshot=snapshot(
            characters=(owned_character,),
            weapons=(owned_weapon,),
            artifacts=(owned_artifact,),
            materials=(owned_material,),
        ),
        observations=observations,
    )

    assert snapshot_evidence.observations == observations
