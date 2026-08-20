import pytest

from teyvat_vision.domain.account import AccountSnapshot, SectionStatus, SnapshotSection
from teyvat_vision.domain.artifact import Artifact, ArtifactSlot, StatValue
from teyvat_vision.domain.character import Character, TalentLevels
from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.domain.instance_identity import OwnedItemId
from teyvat_vision.domain.material import MaterialStack
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
    equipped_to: CanonicalId | None = None,
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
        equipped_to=equipped_to,
    )


def artifact(
    key: str = "15001",
    *,
    instance_key: str = "artifact-000001",
    equipped_to: CanonicalId | None = None,
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
        equipped_to=equipped_to,
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


def test_snapshot_section_preserves_complete_items() -> None:
    item = character()

    section = SnapshotSection(
        status=SectionStatus.COMPLETE,
        items=(item,),
    )

    assert section.status is SectionStatus.COMPLETE
    assert section.items == (item,)


def test_complete_section_can_be_empty() -> None:
    section = SnapshotSection[Character](
        status=SectionStatus.COMPLETE,
        items=(),
    )

    assert section.items == ()


def test_partial_section_can_preserve_known_items() -> None:
    item = character()

    section = SnapshotSection(
        status=SectionStatus.PARTIAL,
        items=(item,),
    )

    assert section.status is SectionStatus.PARTIAL
    assert section.items == (item,)


def test_not_scanned_section_must_be_empty() -> None:
    with pytest.raises(ValueError, match="not scanned"):
        SnapshotSection(
            status=SectionStatus.NOT_SCANNED,
            items=(character(),),
        )


def test_not_scanned_section_explicitly_represents_missing_coverage() -> None:
    section = SnapshotSection[Character](
        status=SectionStatus.NOT_SCANNED,
        items=(),
    )

    assert section.status is SectionStatus.NOT_SCANNED
    assert section.items == ()


def test_account_snapshot_preserves_all_sections() -> None:
    characters = SnapshotSection(
        status=SectionStatus.COMPLETE,
        items=(character(),),
    )
    weapons = SnapshotSection(
        status=SectionStatus.COMPLETE,
        items=(weapon(),),
    )
    artifacts = SnapshotSection(
        status=SectionStatus.COMPLETE,
        items=(artifact(),),
    )
    materials = SnapshotSection(
        status=SectionStatus.COMPLETE,
        items=(material(),),
    )

    snapshot = AccountSnapshot(
        characters=characters,
        weapons=weapons,
        artifacts=artifacts,
        materials=materials,
    )

    assert snapshot.characters == characters
    assert snapshot.weapons == weapons
    assert snapshot.artifacts == artifacts
    assert snapshot.materials == materials


def test_account_snapshot_rejects_duplicate_characters() -> None:
    with pytest.raises(ValueError, match="duplicate character"):
        AccountSnapshot(
            characters=SnapshotSection(
                status=SectionStatus.COMPLETE,
                items=(
                    character("10000002"),
                    character("10000002"),
                ),
            ),
            weapons=SnapshotSection(
                status=SectionStatus.NOT_SCANNED,
                items=(),
            ),
            artifacts=SnapshotSection(
                status=SectionStatus.NOT_SCANNED,
                items=(),
            ),
            materials=SnapshotSection(
                status=SectionStatus.NOT_SCANNED,
                items=(),
            ),
        )


def test_account_snapshot_rejects_duplicate_material_stacks() -> None:
    with pytest.raises(ValueError, match="duplicate material"):
        AccountSnapshot(
            characters=SnapshotSection(
                status=SectionStatus.NOT_SCANNED,
                items=(),
            ),
            weapons=SnapshotSection(
                status=SectionStatus.NOT_SCANNED,
                items=(),
            ),
            artifacts=SnapshotSection(
                status=SectionStatus.NOT_SCANNED,
                items=(),
            ),
            materials=SnapshotSection(
                status=SectionStatus.COMPLETE,
                items=(
                    material("104003", quantity=10),
                    material("104003", quantity=20),
                ),
            ),
        )


def test_account_snapshot_allows_multiple_copies_of_same_weapon_definition() -> None:
    first = weapon(
        "11509",
        instance_key="weapon-000001",
    )
    second = weapon(
        "11509",
        instance_key="weapon-000002",
    )

    snapshot = AccountSnapshot(
        characters=SnapshotSection(
            status=SectionStatus.NOT_SCANNED,
            items=(),
        ),
        weapons=SnapshotSection(
            status=SectionStatus.COMPLETE,
            items=(first, second),
        ),
        artifacts=SnapshotSection(
            status=SectionStatus.NOT_SCANNED,
            items=(),
        ),
        materials=SnapshotSection(
            status=SectionStatus.NOT_SCANNED,
            items=(),
        ),
    )

    assert len(snapshot.weapons.items) == 2
    assert first.identity.definition == second.identity.definition
    assert first.identity != second.identity


def test_account_snapshot_rejects_duplicate_owned_weapon_identity() -> None:
    first = weapon(
        "11509",
        instance_key="weapon-000001",
    )
    duplicate = weapon(
        "11509",
        instance_key="weapon-000001",
    )

    with pytest.raises(ValueError, match="duplicate weapon"):
        AccountSnapshot(
            characters=SnapshotSection(
                status=SectionStatus.NOT_SCANNED,
                items=(),
            ),
            weapons=SnapshotSection(
                status=SectionStatus.COMPLETE,
                items=(first, duplicate),
            ),
            artifacts=SnapshotSection(
                status=SectionStatus.NOT_SCANNED,
                items=(),
            ),
            materials=SnapshotSection(
                status=SectionStatus.NOT_SCANNED,
                items=(),
            ),
        )


def test_account_snapshot_allows_multiple_artifacts_from_same_set() -> None:
    first = artifact(
        "15001",
        instance_key="artifact-000001",
    )
    second = artifact(
        "15001",
        instance_key="artifact-000002",
    )

    snapshot = AccountSnapshot(
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
            items=(first, second),
        ),
        materials=SnapshotSection(
            status=SectionStatus.NOT_SCANNED,
            items=(),
        ),
    )

    assert len(snapshot.artifacts.items) == 2
    assert first.identity.definition == second.identity.definition
    assert first.identity != second.identity


def test_account_snapshot_rejects_duplicate_owned_artifact_identity() -> None:
    first = artifact(
        "15001",
        instance_key="artifact-000001",
    )
    duplicate = artifact(
        "15001",
        instance_key="artifact-000001",
    )

    with pytest.raises(ValueError, match="duplicate artifact"):
        AccountSnapshot(
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
                items=(first, duplicate),
            ),
            materials=SnapshotSection(
                status=SectionStatus.NOT_SCANNED,
                items=(),
            ),
        )


def test_complete_character_section_requires_equipment_owner_to_exist() -> None:
    unknown_owner = character_id("10000099")

    with pytest.raises(ValueError, match="equipped"):
        AccountSnapshot(
            characters=SnapshotSection(
                status=SectionStatus.COMPLETE,
                items=(character("10000002"),),
            ),
            weapons=SnapshotSection(
                status=SectionStatus.COMPLETE,
                items=(weapon(equipped_to=unknown_owner),),
            ),
            artifacts=SnapshotSection(
                status=SectionStatus.COMPLETE,
                items=(),
            ),
            materials=SnapshotSection(
                status=SectionStatus.NOT_SCANNED,
                items=(),
            ),
        )


def test_incomplete_character_section_does_not_claim_owner_is_invalid() -> None:
    unknown_owner = character_id("10000099")

    snapshot = AccountSnapshot(
        characters=SnapshotSection(
            status=SectionStatus.PARTIAL,
            items=(character("10000002"),),
        ),
        weapons=SnapshotSection(
            status=SectionStatus.COMPLETE,
            items=(weapon(equipped_to=unknown_owner),),
        ),
        artifacts=SnapshotSection(
            status=SectionStatus.NOT_SCANNED,
            items=(),
        ),
        materials=SnapshotSection(
            status=SectionStatus.NOT_SCANNED,
            items=(),
        ),
    )

    assert snapshot.weapons.items[0].equipped_to == unknown_owner


def test_complete_character_section_requires_artifact_owner_to_exist() -> None:
    unknown_owner = character_id("10000099")

    with pytest.raises(ValueError, match="equipped"):
        AccountSnapshot(
            characters=SnapshotSection(
                status=SectionStatus.COMPLETE,
                items=(character("10000002"),),
            ),
            weapons=SnapshotSection(
                status=SectionStatus.NOT_SCANNED,
                items=(),
            ),
            artifacts=SnapshotSection(
                status=SectionStatus.COMPLETE,
                items=(artifact(equipped_to=unknown_owner),),
            ),
            materials=SnapshotSection(
                status=SectionStatus.NOT_SCANNED,
                items=(),
            ),
        )


def test_incomplete_character_section_does_not_claim_artifact_owner_is_invalid() -> None:
    unknown_owner = character_id("10000099")

    snapshot = AccountSnapshot(
        characters=SnapshotSection(
            status=SectionStatus.PARTIAL,
            items=(character("10000002"),),
        ),
        weapons=SnapshotSection(
            status=SectionStatus.NOT_SCANNED,
            items=(),
        ),
        artifacts=SnapshotSection(
            status=SectionStatus.COMPLETE,
            items=(artifact(equipped_to=unknown_owner),),
        ),
        materials=SnapshotSection(
            status=SectionStatus.NOT_SCANNED,
            items=(),
        ),
    )

    assert snapshot.artifacts.items[0].equipped_to == unknown_owner
