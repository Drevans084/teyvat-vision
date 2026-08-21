from teyvat_vision.domain.account import (
    AccountSnapshot,
    SectionStatus,
    SnapshotSection,
)
from teyvat_vision.domain.artifact import Artifact, ArtifactSlot, StatValue
from teyvat_vision.domain.character import Character, TalentLevels
from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.domain.instance_identity import OwnedItemId
from teyvat_vision.domain.material import MaterialStack
from teyvat_vision.domain.weapon import Weapon
from teyvat_vision.game_data.dataset import StaticGameData
from teyvat_vision.game_data.records import (
    ArtifactSetDefinition,
    CharacterDefinition,
    MaterialDefinition,
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
WEAPON_DEFINITION_ID = CanonicalId(
    kind=EntityKind.WEAPON,
    key="11509",
)
ARTIFACT_SET_ID = CanonicalId(
    kind=EntityKind.ARTIFACT_SET,
    key="15001",
)
MATERIAL_ID = CanonicalId(
    kind=EntityKind.MATERIAL,
    key="104003",
)


def static_game_data() -> StaticGameData:
    return StaticGameData(
        version="6.8",
        characters=(
            CharacterDefinition(
                identity=CHARACTER_ID,
            ),
        ),
        weapons=(
            WeaponDefinition(
                identity=WEAPON_DEFINITION_ID,
            ),
        ),
        artifact_sets=(
            ArtifactSetDefinition(
                identity=ARTIFACT_SET_ID,
            ),
        ),
        materials=(
            MaterialDefinition(
                identity=MATERIAL_ID,
            ),
        ),
    )


def snapshot(
    *,
    character_id: CanonicalId = CHARACTER_ID,
    weapon_definition_id: CanonicalId = WEAPON_DEFINITION_ID,
    artifact_set_id: CanonicalId = ARTIFACT_SET_ID,
    material_id: CanonicalId = MATERIAL_ID,
) -> AccountSnapshot:
    return AccountSnapshot(
        characters=SnapshotSection(
            status=SectionStatus.COMPLETE,
            items=(
                Character(
                    identity=character_id,
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
                        definition=weapon_definition_id,
                        instance_key="weapon-1",
                    ),
                    level=90,
                    ascension=6,
                    refinement=1,
                    locked=False,
                ),
            ),
        ),
        artifacts=SnapshotSection(
            status=SectionStatus.COMPLETE,
            items=(
                Artifact(
                    identity=OwnedItemId(
                        definition=artifact_set_id,
                        instance_key="artifact-1",
                    ),
                    slot=ArtifactSlot.FLOWER,
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
            status=SectionStatus.COMPLETE,
            items=(
                MaterialStack(
                    identity=material_id,
                    quantity=1,
                ),
            ),
        ),
    )


def test_snapshot_with_known_static_identities_is_valid() -> None:
    result = validate_snapshot_against_game_data(
        snapshot(),
        static_game_data(),
    )

    assert result.is_valid
    assert result.issues == ()


def test_snapshot_reports_unknown_character() -> None:
    unknown = CanonicalId(
        kind=EntityKind.CHARACTER,
        key="unknown-character",
    )

    result = validate_snapshot_against_game_data(
        snapshot(character_id=unknown),
        static_game_data(),
    )

    assert len(result.errors) == 1

    issue = result.errors[0]

    assert issue.code == "unknown_character"
    assert issue.severity is ValidationSeverity.ERROR
    assert issue.subject == unknown
    assert issue.field == "identity"


def test_snapshot_reports_unknown_weapon_definition() -> None:
    unknown = CanonicalId(
        kind=EntityKind.WEAPON,
        key="unknown-weapon",
    )

    account = snapshot(
        weapon_definition_id=unknown,
    )

    result = validate_snapshot_against_game_data(
        account,
        static_game_data(),
    )

    assert len(result.errors) == 1

    issue = result.errors[0]

    assert issue.code == "unknown_weapon"
    assert issue.severity is ValidationSeverity.ERROR
    assert issue.subject == account.weapons.items[0].identity
    assert issue.field == "identity.definition"


def test_snapshot_reports_unknown_artifact_set_definition() -> None:
    unknown = CanonicalId(
        kind=EntityKind.ARTIFACT_SET,
        key="unknown-artifact-set",
    )

    account = snapshot(
        artifact_set_id=unknown,
    )

    result = validate_snapshot_against_game_data(
        account,
        static_game_data(),
    )

    assert len(result.errors) == 1

    issue = result.errors[0]

    assert issue.code == "unknown_artifact_set"
    assert issue.severity is ValidationSeverity.ERROR
    assert issue.subject == account.artifacts.items[0].identity
    assert issue.field == "identity.definition"


def test_snapshot_reports_unknown_material() -> None:
    unknown = CanonicalId(
        kind=EntityKind.MATERIAL,
        key="unknown-material",
    )

    result = validate_snapshot_against_game_data(
        snapshot(material_id=unknown),
        static_game_data(),
    )

    assert len(result.errors) == 1

    issue = result.errors[0]

    assert issue.code == "unknown_material"
    assert issue.severity is ValidationSeverity.ERROR
    assert issue.subject == unknown
    assert issue.field == "identity"
