import pytest

from teyvat_vision.domain.account import AccountSnapshot, SectionStatus, SnapshotSection
from teyvat_vision.domain.artifact import Artifact, ArtifactSlot, StatValue
from teyvat_vision.domain.character import Character, TalentLevels
from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.domain.instance_identity import OwnedItemId
from teyvat_vision.domain.material import MaterialStack
from teyvat_vision.domain.weapon import Weapon


def character_id(key: str) -> CanonicalId:
    return CanonicalId(
        kind=EntityKind.CHARACTER,
        key=key,
    )


def character(key: str) -> Character:
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
    instance_key: str,
    *,
    equipped_to: CanonicalId | None = None,
) -> Weapon:
    return Weapon(
        identity=OwnedItemId(
            definition=CanonicalId(
                kind=EntityKind.WEAPON,
                key="11509",
            ),
            instance_key=instance_key,
        ),
        level=90,
        ascension=6,
        refinement=1,
        locked=True,
        equipped_to=equipped_to,
    )


def artifact(
    instance_key: str,
    *,
    slot: ArtifactSlot,
    equipped_to: CanonicalId | None = None,
) -> Artifact:
    return Artifact(
        identity=OwnedItemId(
            definition=CanonicalId(
                kind=EntityKind.ARTIFACT_SET,
                key="15001",
            ),
            instance_key=instance_key,
        ),
        slot=slot,
        rarity=5,
        level=20,
        main_stat=StatValue(
            key="hp",
            value=4780.0,
        ),
        substats=(),
        locked=True,
        equipped_to=equipped_to,
    )


def snapshot(
    *,
    characters: tuple[Character, ...],
    weapons: tuple[Weapon, ...] = (),
    artifacts: tuple[Artifact, ...] = (),
    character_status: SectionStatus = SectionStatus.COMPLETE,
) -> AccountSnapshot:
    return AccountSnapshot(
        characters=SnapshotSection(
            status=character_status,
            items=characters,
        ),
        weapons=SnapshotSection(
            status=SectionStatus.COMPLETE,
            items=weapons,
        ),
        artifacts=SnapshotSection(
            status=SectionStatus.COMPLETE,
            items=artifacts,
        ),
        materials=SnapshotSection[MaterialStack](
            status=SectionStatus.NOT_SCANNED,
            items=(),
        ),
    )


def test_account_snapshot_rejects_two_weapons_equipped_to_same_character() -> None:
    owner = character_id("10000002")

    with pytest.raises(ValueError, match="multiple weapons"):
        snapshot(
            characters=(character("10000002"),),
            weapons=(
                weapon("weapon-000001", equipped_to=owner),
                weapon("weapon-000002", equipped_to=owner),
            ),
        )


def test_account_snapshot_allows_weapons_equipped_to_different_characters() -> None:
    first_owner = character_id("10000002")
    second_owner = character_id("10000003")

    account_snapshot = snapshot(
        characters=(
            character("10000002"),
            character("10000003"),
        ),
        weapons=(
            weapon("weapon-000001", equipped_to=first_owner),
            weapon("weapon-000002", equipped_to=second_owner),
        ),
    )

    assert account_snapshot.weapons.items[0].equipped_to == first_owner
    assert account_snapshot.weapons.items[1].equipped_to == second_owner


def test_account_snapshot_allows_multiple_unequipped_weapons() -> None:
    account_snapshot = snapshot(
        characters=(character("10000002"),),
        weapons=(
            weapon("weapon-000001"),
            weapon("weapon-000002"),
        ),
    )

    assert len(account_snapshot.weapons.items) == 2


def test_account_snapshot_rejects_two_artifacts_in_same_slot_on_same_character() -> None:
    owner = character_id("10000002")

    with pytest.raises(ValueError, match="multiple artifacts"):
        snapshot(
            characters=(character("10000002"),),
            artifacts=(
                artifact(
                    "artifact-000001",
                    slot=ArtifactSlot.FLOWER,
                    equipped_to=owner,
                ),
                artifact(
                    "artifact-000002",
                    slot=ArtifactSlot.FLOWER,
                    equipped_to=owner,
                ),
            ),
        )


def test_account_snapshot_allows_different_artifact_slots_on_same_character() -> None:
    owner = character_id("10000002")

    account_snapshot = snapshot(
        characters=(character("10000002"),),
        artifacts=(
            artifact(
                "artifact-000001",
                slot=ArtifactSlot.FLOWER,
                equipped_to=owner,
            ),
            artifact(
                "artifact-000002",
                slot=ArtifactSlot.PLUME,
                equipped_to=owner,
            ),
        ),
    )

    assert len(account_snapshot.artifacts.items) == 2


def test_account_snapshot_allows_same_artifact_slot_on_different_characters() -> None:
    first_owner = character_id("10000002")
    second_owner = character_id("10000003")

    account_snapshot = snapshot(
        characters=(
            character("10000002"),
            character("10000003"),
        ),
        artifacts=(
            artifact(
                "artifact-000001",
                slot=ArtifactSlot.FLOWER,
                equipped_to=first_owner,
            ),
            artifact(
                "artifact-000002",
                slot=ArtifactSlot.FLOWER,
                equipped_to=second_owner,
            ),
        ),
    )

    assert len(account_snapshot.artifacts.items) == 2


def test_weapon_assignment_conflict_is_invalid_with_partial_character_coverage() -> None:
    unknown_owner = character_id("10000099")

    with pytest.raises(ValueError, match="multiple weapons"):
        snapshot(
            characters=(character("10000002"),),
            character_status=SectionStatus.PARTIAL,
            weapons=(
                weapon("weapon-000001", equipped_to=unknown_owner),
                weapon("weapon-000002", equipped_to=unknown_owner),
            ),
        )


def test_artifact_slot_conflict_is_invalid_with_partial_character_coverage() -> None:
    unknown_owner = character_id("10000099")

    with pytest.raises(ValueError, match="multiple artifacts"):
        snapshot(
            characters=(character("10000002"),),
            character_status=SectionStatus.PARTIAL,
            artifacts=(
                artifact(
                    "artifact-000001",
                    slot=ArtifactSlot.CIRCLET,
                    equipped_to=unknown_owner,
                ),
                artifact(
                    "artifact-000002",
                    slot=ArtifactSlot.CIRCLET,
                    equipped_to=unknown_owner,
                ),
            ),
        )
