from typing import Any

import pytest

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


def character() -> Character:
    return Character(
        identity=character_id(),
        level=90,
        ascension=6,
        constellation=0,
        talents=TalentLevels(
            normal=9,
            skill=9,
            burst=9,
        ),
    )


def weapon() -> Weapon:
    return Weapon(
        identity=weapon_id(),
        level=90,
        ascension=6,
        refinement=1,
        locked=True,
    )


def artifact() -> Artifact:
    return Artifact(
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
    )


def material() -> MaterialStack:
    return MaterialStack(
        identity=material_id(),
        quantity=25,
    )


def snapshot() -> AccountSnapshot:
    return AccountSnapshot(
        characters=SnapshotSection(
            status=SectionStatus.COMPLETE,
            items=(character(),),
        ),
        weapons=SnapshotSection(
            status=SectionStatus.COMPLETE,
            items=(weapon(),),
        ),
        artifacts=SnapshotSection(
            status=SectionStatus.COMPLETE,
            items=(artifact(),),
        ),
        materials=SnapshotSection(
            status=SectionStatus.COMPLETE,
            items=(material(),),
        ),
    )


def provenance() -> Provenance:
    return Provenance(
        kind=ProvenanceKind.MANUAL_VERIFIED,
        source="verified-fixture",
    )


def observation(
    *,
    subject: CanonicalId | OwnedItemId,
    field: str,
    value: Any,
) -> Observation[Any]:
    return Observation(
        target=ObservationTarget(
            subject=subject,
            field=field,
        ),
        value=value,
        provenance=provenance(),
    )


def snapshot_evidence(
    observation: Observation[Any],
) -> SnapshotEvidence:
    return SnapshotEvidence(
        snapshot=snapshot(),
        observations=(observation,),
    )


def test_observation_target_can_exist_before_snapshot_field_validation() -> None:
    target = ObservationTarget(
        subject=character_id(),
        field="future_field",
    )

    assert target.field == "future_field"


@pytest.mark.parametrize(
    "field",
    [
        "level",
        "ascension",
        "constellation",
        "custom_name",
        "talents.normal",
        "talents.skill",
        "talents.burst",
    ],
)
def test_snapshot_evidence_accepts_supported_character_field(field: str) -> None:
    evidence = snapshot_evidence(
        observation(
            subject=character_id(),
            field=field,
            value=90,
        )
    )

    assert evidence.observations[0].target.field == field


def test_snapshot_evidence_rejects_unsupported_character_field() -> None:
    with pytest.raises(ValueError, match="observation field"):
        snapshot_evidence(
            observation(
                subject=character_id(),
                field="refinement",
                value=1,
            )
        )


def test_snapshot_evidence_rejects_character_talents_aggregate_field() -> None:
    with pytest.raises(ValueError, match="observation field"):
        snapshot_evidence(
            observation(
                subject=character_id(),
                field="talents",
                value=(9, 9, 9),
            )
        )


@pytest.mark.parametrize(
    "field",
    [
        "level",
        "ascension",
        "refinement",
        "locked",
        "equipped_to",
    ],
)
def test_snapshot_evidence_accepts_supported_weapon_field(field: str) -> None:
    evidence = snapshot_evidence(
        observation(
            subject=weapon_id(),
            field=field,
            value=90,
        )
    )

    assert evidence.observations[0].target.field == field


def test_snapshot_evidence_rejects_unsupported_weapon_field() -> None:
    with pytest.raises(ValueError, match="observation field"):
        snapshot_evidence(
            observation(
                subject=weapon_id(),
                field="constellation",
                value=0,
            )
        )


def test_snapshot_evidence_accepts_material_quantity_field() -> None:
    evidence = snapshot_evidence(
        observation(
            subject=material_id(),
            field="quantity",
            value=25,
        )
    )

    assert evidence.observations[0].target.field == "quantity"


def test_snapshot_evidence_rejects_unsupported_material_field() -> None:
    with pytest.raises(ValueError, match="observation field"):
        snapshot_evidence(
            observation(
                subject=material_id(),
                field="level",
                value=1,
            )
        )


@pytest.mark.parametrize(
    "field",
    [
        "slot",
        "rarity",
        "level",
        "main_stat.key",
        "main_stat.value",
        "locked",
        "equipped_to",
    ],
)
def test_snapshot_evidence_accepts_supported_artifact_field(field: str) -> None:
    evidence = snapshot_evidence(
        observation(
            subject=artifact_id(),
            field=field,
            value=20,
        )
    )

    assert evidence.observations[0].target.field == field


def test_snapshot_evidence_accepts_existing_artifact_substat_field() -> None:
    evidence = snapshot_evidence(
        observation(
            subject=artifact_id(),
            field="substats.crit_rate",
            value=3.9,
        )
    )

    assert evidence.observations[0].target.field == "substats.crit_rate"


def test_snapshot_evidence_rejects_absent_artifact_substat_field() -> None:
    with pytest.raises(ValueError, match="observation field"):
        snapshot_evidence(
            observation(
                subject=artifact_id(),
                field="substats.energy_recharge",
                value=5.2,
            )
        )


def test_snapshot_evidence_rejects_bare_artifact_substats_field() -> None:
    with pytest.raises(ValueError, match="observation field"):
        snapshot_evidence(
            observation(
                subject=artifact_id(),
                field="substats",
                value=(),
            )
        )


def test_snapshot_evidence_rejects_malformed_artifact_substat_field() -> None:
    with pytest.raises(ValueError, match="observation field"):
        snapshot_evidence(
            observation(
                subject=artifact_id(),
                field="substats.",
                value=3.9,
            )
        )


def test_snapshot_evidence_rejects_character_only_field_for_artifact() -> None:
    with pytest.raises(ValueError, match="observation field"):
        snapshot_evidence(
            observation(
                subject=artifact_id(),
                field="constellation",
                value=0,
            )
        )
