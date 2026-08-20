import pytest

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.game_data.dataset import StaticGameData
from teyvat_vision.game_data.records import (
    ArtifactSetDefinition,
    CharacterDefinition,
    MaterialDefinition,
    WeaponDefinition,
)


def character(key: str = "10000002") -> CharacterDefinition:
    return CharacterDefinition(
        identity=CanonicalId(
            kind=EntityKind.CHARACTER,
            key=key,
        )
    )


def weapon(key: str = "11509") -> WeaponDefinition:
    return WeaponDefinition(
        identity=CanonicalId(
            kind=EntityKind.WEAPON,
            key=key,
        )
    )


def artifact_set(key: str = "15001") -> ArtifactSetDefinition:
    return ArtifactSetDefinition(
        identity=CanonicalId(
            kind=EntityKind.ARTIFACT_SET,
            key=key,
        )
    )


def material(key: str = "104003") -> MaterialDefinition:
    return MaterialDefinition(
        identity=CanonicalId(
            kind=EntityKind.MATERIAL,
            key=key,
        )
    )


def dataset(
    *,
    version: str = "6.8",
    characters: tuple[CharacterDefinition, ...] = (),
    weapons: tuple[WeaponDefinition, ...] = (),
    artifact_sets: tuple[ArtifactSetDefinition, ...] = (),
    materials: tuple[MaterialDefinition, ...] = (),
) -> StaticGameData:
    return StaticGameData(
        version=version,
        characters=characters,
        weapons=weapons,
        artifact_sets=artifact_sets,
        materials=materials,
    )


def test_static_game_data_preserves_version_and_all_collections() -> None:
    characters = (character(),)
    weapons = (weapon(),)
    artifact_sets = (artifact_set(),)
    materials = (material(),)

    game_data = dataset(
        characters=characters,
        weapons=weapons,
        artifact_sets=artifact_sets,
        materials=materials,
    )

    assert game_data.version == "6.8"
    assert game_data.characters == characters
    assert game_data.weapons == weapons
    assert game_data.artifact_sets == artifact_sets
    assert game_data.materials == materials


def test_static_game_data_allows_empty_collections() -> None:
    game_data = dataset()

    assert game_data.characters == ()
    assert game_data.weapons == ()
    assert game_data.artifact_sets == ()
    assert game_data.materials == ()


def test_static_game_data_rejects_blank_version() -> None:
    with pytest.raises(ValueError, match="version"):
        dataset(version="")


def test_static_game_data_rejects_whitespace_only_version() -> None:
    with pytest.raises(ValueError, match="version"):
        dataset(version="   ")


def test_static_game_data_rejects_version_with_surrounding_whitespace() -> None:
    with pytest.raises(ValueError, match="version"):
        dataset(version=" 6.8 ")


def test_static_game_data_rejects_duplicate_character_identity() -> None:
    with pytest.raises(ValueError, match="duplicate character"):
        dataset(
            characters=(
                character("10000002"),
                character("10000002"),
            )
        )


def test_static_game_data_rejects_duplicate_weapon_identity() -> None:
    with pytest.raises(ValueError, match="duplicate weapon"):
        dataset(
            weapons=(
                weapon("11509"),
                weapon("11509"),
            )
        )


def test_static_game_data_rejects_duplicate_artifact_set_identity() -> None:
    with pytest.raises(ValueError, match="duplicate artifact"):
        dataset(
            artifact_sets=(
                artifact_set("15001"),
                artifact_set("15001"),
            )
        )


def test_static_game_data_rejects_duplicate_material_identity() -> None:
    with pytest.raises(ValueError, match="duplicate material"):
        dataset(
            materials=(
                material("104003"),
                material("104003"),
            )
        )


def test_static_game_data_allows_same_key_across_different_entity_kinds() -> None:
    shared_key = "12345"

    game_data = dataset(
        characters=(character(shared_key),),
        weapons=(weapon(shared_key),),
        artifact_sets=(artifact_set(shared_key),),
        materials=(material(shared_key),),
    )

    identities = {
        game_data.characters[0].identity,
        game_data.weapons[0].identity,
        game_data.artifact_sets[0].identity,
        game_data.materials[0].identity,
    }

    assert len(identities) == 4


def test_static_game_data_preserves_case_sensitive_version() -> None:
    game_data = dataset(version="6.8-RC1")

    assert game_data.version == "6.8-RC1"
