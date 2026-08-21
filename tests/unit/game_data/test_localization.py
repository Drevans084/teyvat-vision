import pytest

from teyvat_vision.game_data.localization import LocalizedName


def test_localized_name_preserves_locale_and_value() -> None:
    name = LocalizedName(
        locale="en-US",
        value="Kaedehara Kazuha",
    )

    assert name.locale == "en-US"
    assert name.value == "Kaedehara Kazuha"


@pytest.mark.parametrize(
    "locale",
    [
        "",
        "   ",
    ],
)
def test_localized_name_rejects_blank_locale(locale: str) -> None:
    with pytest.raises(ValueError, match="locale"):
        LocalizedName(
            locale=locale,
            value="Kaedehara Kazuha",
        )


def test_localized_name_rejects_locale_with_surrounding_whitespace() -> None:
    with pytest.raises(ValueError, match="locale"):
        LocalizedName(
            locale=" en-US ",
            value="Kaedehara Kazuha",
        )


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
    ],
)
def test_localized_name_rejects_blank_value(value: str) -> None:
    with pytest.raises(ValueError, match="value"):
        LocalizedName(
            locale="en-US",
            value=value,
        )


def test_localized_name_rejects_value_with_surrounding_whitespace() -> None:
    with pytest.raises(ValueError, match="value"):
        LocalizedName(
            locale="en-US",
            value=" Kaedehara Kazuha ",
        )


def test_localized_name_preserves_case() -> None:
    name = LocalizedName(
        locale="en-US",
        value="Kaedehara Kazuha",
    )

    assert name.value == "Kaedehara Kazuha"


def test_localized_name_preserves_unicode() -> None:
    name = LocalizedName(
        locale="ja-JP",
        value="楓原万葉",
    )

    assert name.value == "楓原万葉"


def test_localized_name_preserves_punctuation() -> None:
    name = LocalizedName(
        locale="en-US",
        value="Toukabou Shigure",
    )

    assert name.value == "Toukabou Shigure"
