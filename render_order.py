from enum import auto, Enum

class RenderOrder(Enum):
    TRAP = auto()
    GOLD = auto()
    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()
