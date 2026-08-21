from teyvat_vision.domain.account import (
    AccountSnapshot,
    SectionStatus,
    SnapshotSection,
)
from teyvat_vision.domain.character import Character, TalentLevels
from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.domain.instance_identity import OwnedItemId
from teyvat_vision.domain.weapon import Weapon
from teyvat_vision.game_data.classification import WeaponType
from teyvat_vision.game_data.dataset import StaticGameData
from teyvat_vision.game_data.records import (
    CharacterDefinition,
    WeaponDefinition,
)
from teyvat_vision.game_data.validation import (
    ValidationSeverity,
    validate_snapshot_against_game_data,
)


CHARACTER_ID = CanonicalId(
    kind=EntityKind.CHARACTER,
    key="10000047",
)

WEAPON_ID = CanonicalId(
    kind=EntityKind.WEAPON,
    key="11509",
)


def game_data(
    *,
    character_weapon_type: WeaponType | None,
    weapon_type: WeaponType | None,
) -> StaticGameData:
    return StaticGameData(
        version="6.8",
        characters=(
            CharacterDefinition(
                identity=CHARACTER_ID,
                weapon_type=character_weapon_type,
            ),
        ),
        weapons=(
            WeaponDefinition(
                identity=WEAPON_ID,
                weapon_type=weapon_type,
            ),
        ),
        artifact_sets=(),
        materials=(),
    )


def snapshot(
    *,
    equipped: bool = True,
) -> AccountSnapshot:
    return AccountSnapshot(
        characters=SnapshotSection(
            status=SectionStatus.COMPLETE,
            items=(
                Character(
                    identity=CHARACTER_ID,
                    level=90,
                    ascension=6,
                    constellation=0,
                    talents=TalentLevels(
                        normal=1,
                        skill=1,
                        burst=1,
                    ),
                ),
            ),
        ),
        weapons=SnapshotSection(
            status=SectionStatus.COMPLETE,
            items=(
                Weapon(
                    identity=OwnedItemId(
                        definition=WEAPON_ID,
                        instance_key="weapon-1",
                    ),
                    level=90,
                    ascension=6,
                    refinement=1,
                    locked=False,
                    equipped_to=CHARACTER_ID if equipped else None,
                ),
            ),
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


def test_matching_equipped_weapon_type_is_valid() -> None:
    result = validate_snapshot_against_game_data(
        snapshot(),
        game_data(
            character_weapon_type=WeaponType.SWORD,
            weapon_type=WeaponType.SWORD,
        ),
    )

    assert result.is_valid
    assert result.issues == ()


def test_mismatched_equipped_weapon_type_is_invalid() -> None:
    account = snapshot()

    result = validate_snapshot_against_game_data(
        account,
        game_data(
            character_weapon_type=WeaponType.BOW,
            weapon_type=WeaponType.SWORD,
        ),
    )

    assert len(result.errors) == 1

    issue = result.errors[0]

    assert issue.code == "weapon_type_mismatch"
    assert issue.severity is ValidationSeverity.ERROR
    assert issue.subject == account.weapons.items[0].identity
    assert issue.field == "equipped_to"


def test_unknown_character_weapon_type_does_not_fabricate_mismatch() -> None:
    result = validate_snapshot_against_game_data(
        snapshot(),
        game_data(
            character_weapon_type=None,
            weapon_type=WeaponType.SWORD,
        ),
    )

    assert result.is_valid
    assert result.issues == ()


def test_unknown_weapon_type_does_not_fabricate_mismatch() -> None:
    result = validate_snapshot_against_game_data(
        snapshot(),
        game_data(
            character_weapon_type=WeaponType.SWORD,
            weapon_type=None,
        ),
    )

    assert result.is_valid
    assert result.issues == ()


def test_unequipped_weapon_does_not_require_character_compatibility() -> None:
    result = validate_snapshot_against_game_data(
        snapshot(equipped=False),
        game_data(
            character_weapon_type=WeaponType.BOW,
            weapon_type=WeaponType.SWORD,
        ),
    )

    assert result.is_valid
    assert result.issues == ()
