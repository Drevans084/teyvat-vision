"""Provider-independent localization primitives for static game data."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LocalizedName:
    """One localized display name for a static game-data entity."""

    locale: str
    value: str

    def __post_init__(self) -> None:
        if not self.locale.strip():
            raise ValueError("locale must not be blank")

        if self.locale != self.locale.strip():
            raise ValueError("locale must not contain surrounding whitespace")

        if not self.value.strip():
            raise ValueError("value must not be blank")

        if self.value != self.value.strip():
            raise ValueError("value must not contain surrounding whitespace")
