from __future__ import annotations

from typing import List, Any
import random

from components.ai import HostileEnemy
from components.fighter import Fighter
from components.consumable import HealingConsumable
from components.inventory import Inventory
from components.ability import Omnipotent, SimpleAbility, AllCommands
from entity import Actor, Item, Amulet
import colors

# A "Family" of comparable-value items; useful for uniformly
#  sampling from a set of similar objects
class Family():
    def __init__(self,items:List[Any]):
        self.items = items
    def sample(self) -> Any:
        return random.choice(self.items)
    # I need it to be hashable for the sampling function in procgen to work
    def __str__(self) -> str:
        return "Family: " + ",".join([str(i) for i in self.items])
    def __hash__(self) -> int:
        return hash(str(self))


# TODO Multiple differing starting classes
starting_abilities = ["h","j","k","l","yy","y","d"]

player = Actor(
    char="@",
    color=colors.default_fg,
    name="player",
    summary="You, the player.",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=10,AC=0,strength=2),
    abilities=[SimpleAbility(s) for s in starting_abilities],
    inventory=Inventory(capacity=35),
    max_range=5,
    fov_radius=12,
)

# Enemies ==================================================================

# Will follow player by sight if possible
nano = Actor(
    char="n",
    color=colors.nano,
    name="nano",
    summary="A harmless text editor.",
    ai_cls=HostileEnemy,
    fov_radius=11,
    fighter=Fighter(hp=4,AC=0,strength=3,attack_text="bit"),
    hp_buff=True
)
# Remains stationary until player seen, then tracks indefinitely
ed = Actor(
    char="e",
    color=colors.ed,
    name="ed",
    summary="ed is the standard text editor.",
    ai_cls=HostileEnemy,
    fov_radius=11,
    needs_los=False,
    fighter=Fighter(hp=2,AC=0,strength=2,attack_text="?")
    # TODO Ed should track you, while nano doesn't.
)

# Define items here =======================================================


# Dictionary of amulet items
amulet = {}
for command in ["h","j","k","l","H","M","L","0","$","`","'","dd","t","f","w","e",";","u","m"]:
    amulet[command] = Amulet(ability_str=command)
# Families of aforementioned amulets
basic_movement_amulet = Family([amulet[s] for s in "hjkl"])
capital_amulet = Family([amulet[s] for s in "HML0$"])
mark_amulet = Family([amulet[s] for s in "m`'"])
f_amulet = Family([amulet[s] for s in "tfwe;"])
special_amulet = Family([amulet[s] for s in ["dd","u"]])

# Arquebus - lets you d without moving
arquebus = Item(
    char=")",
    name="arquebus",
    summary="A ranged weapon.",
    ability = SimpleAbility("ranged")
)

# TODO Spellbooks?
