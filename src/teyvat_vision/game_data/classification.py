"""Canonical static game-data classifications for Teyvat Vision."""

from enum import Enum, StrEnum


class WeaponType(StrEnum):
    """Canonical weapon classes used by characters and weapons."""

    SWORD = "sword"
    CLAYMORE = "claymore"
    POLEARM = "polearm"
    BOW = "bow"
    CATALYST = "catalyst"


class Rarity(Enum):
    """Canonical star-rarity values for static game data."""

    ONE_STAR = 1
    TWO_STAR = 2
    THREE_STAR = 3
    FOUR_STAR = 4
    FIVE_STAR = 5
