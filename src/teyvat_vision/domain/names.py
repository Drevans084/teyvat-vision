"""User-assigned name primitives for Teyvat Vision.

Custom names preserve the exact text entered by the player. Case is meaningful
and must never be normalized implicitly.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CustomName:
    """An exact, case-sensitive user-assigned name."""

    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("name must not be blank")

        if self.value != self.value.strip():
            raise ValueError("name must not contain surrounding whitespace")

    def __str__(self) -> str:
        return self.value
