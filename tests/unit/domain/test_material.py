import pytest

from teyvat_vision.domain.identity import CanonicalId, EntityKind
from teyvat_vision.domain.material import MaterialStack


def material_id(key: str = "104003") -> CanonicalId:
    return CanonicalId(
        kind=EntityKind.MATERIAL,
        key=key,
    )


def test_material_stack_preserves_valid_account_state() -> None:
    material = MaterialStack(
        identity=material_id(),
        quantity=157,
    )

    assert material.identity == material_id()
    assert material.quantity == 157


def test_material_stack_rejects_non_material_identity() -> None:
    with pytest.raises(ValueError, match="material"):
        MaterialStack(
            identity=CanonicalId(
                kind=EntityKind.WEAPON,
                key="11509",
            ),
            quantity=10,
        )


@pytest.mark.parametrize("quantity", [0, -1])
def test_material_stack_rejects_non_positive_quantity(quantity: int) -> None:
    with pytest.raises(ValueError, match="quantity"):
        MaterialStack(
            identity=material_id(),
            quantity=quantity,
        )


@pytest.mark.parametrize(
    "quantity",
    [
        True,
        False,
        1.0,
        "1",
        None,
    ],
)
def test_material_stack_rejects_non_integer_quantity(quantity: object) -> None:
    with pytest.raises(ValueError, match="quantity"):
        MaterialStack(
            identity=material_id(),
            quantity=quantity,  # type: ignore[arg-type]
        )
