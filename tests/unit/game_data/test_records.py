import pytest

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.game_data.records import (
    ArtifactSetDefinition,
    CharacterDefinition,
    MaterialDefinition,
    WeaponDefinition,
)


def canonical_id(
    kind: EntityKind,
    key: str,
) -> CanonicalId:
    return CanonicalId(
        kind=kind,
        key=key,
    )


def test_character_definition_preserves_character_identity() -> None:
    identity = canonical_id(
        EntityKind.CHARACTER,
        "10000002",
    )

    definition = CharacterDefinition(identity=identity)

    assert definition.identity == identity


def test_character_definition_rejects_non_character_identity() -> None:
    with pytest.raises(ValueError, match="character"):
        CharacterDefinition(
            identity=canonical_id(
                EntityKind.WEAPON,
                "11509",
            )
        )


def test_weapon_definition_preserves_weapon_identity() -> None:
    identity = canonical_id(
        EntityKind.WEAPON,
        "11509",
    )

    definition = WeaponDefinition(identity=identity)

    assert definition.identity == identity


def test_weapon_definition_rejects_non_weapon_identity() -> None:
    with pytest.raises(ValueError, match="weapon"):
        WeaponDefinition(
            identity=canonical_id(
                EntityKind.CHARACTER,
                "10000002",
            )
        )


def test_artifact_set_definition_preserves_artifact_set_identity() -> None:
    identity = canonical_id(
        EntityKind.ARTIFACT_SET,
        "15001",
    )

    definition = ArtifactSetDefinition(identity=identity)

    assert definition.identity == identity


def test_artifact_set_definition_rejects_non_artifact_set_identity() -> None:
    with pytest.raises(ValueError, match="artifact"):
        ArtifactSetDefinition(
            identity=canonical_id(
                EntityKind.MATERIAL,
                "104003",
            )
        )


def test_material_definition_preserves_material_identity() -> None:
    identity = canonical_id(
        EntityKind.MATERIAL,
        "104003",
    )

    definition = MaterialDefinition(identity=identity)

    assert definition.identity == identity


def test_material_definition_rejects_non_material_identity() -> None:
    with pytest.raises(ValueError, match="material"):
        MaterialDefinition(
            identity=canonical_id(
                EntityKind.CHARACTER,
                "10000002",
            )
        )
