import pytest

from teyvat_vision.domain.names import CustomName


def test_custom_name_preserves_exact_value() -> None:
    name = CustomName("YETI084")

    assert name.value == "YETI084"


def test_custom_names_are_case_sensitive() -> None:
    upper = CustomName("Traveler")
    lower = CustomName("traveler")

    assert upper != lower
    assert upper.value == "Traveler"
    assert lower.value == "traveler"


def test_custom_name_preserves_internal_spaces() -> None:
    name = CustomName("My Traveler")

    assert name.value == "My Traveler"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
        "\t",
        "\n",
    ],
)
def test_custom_name_rejects_blank_values(value: str) -> None:
    with pytest.raises(ValueError, match="name"):
        CustomName(value)


def test_custom_name_rejects_surrounding_whitespace() -> None:
    with pytest.raises(ValueError, match="whitespace"):
        CustomName(" Traveler ")


def test_custom_name_is_hashable() -> None:
    name = CustomName("Traveler")

    names = {name}

    assert name in names
