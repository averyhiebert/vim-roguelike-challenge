from components.ai import HostileEnemy
from components.fighter import Fighter
from components.consumable import HealingConsumable
from components.inventory import Inventory
from components.ability import Omnipotent, SimpleAbility, AllCommands
from entity import Actor, Item, Amulet
import colors

# TODO Multiple differing starting classes
starting_abilities = ["h","j","k","l","yy","y","d"]

player = Actor(
    char="@",
    color=colors.default_fg,
    name="player",
    summary="You, the player.",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=30,AC=10,to_hit="1d20",damage="1d20"),
    #abilities=[AllCommands()],
    #abilities=[Omnipotent()],
    abilities=[SimpleAbility(s) for s in starting_abilities],
    inventory=Inventory(capacity=35)
)

# Define enemy types here
nano = Actor(
    char="n",
    color=colors.nano,
    name="nano",
    summary="A harmless text editor.",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=8,AC=8,to_hit="1d20",damage="1d4")
)
ed = Actor(
    char="e",
    color=colors.ed,
    name="ed",
    summary="An ? known for ? and ?",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=8,AC=8,to_hit="1d12",damage="1d6")
)

# Define items here =======================================================

# Dictionary of amulet items
amulet = {}
for command in ["h","j","k","l","H","M","L","0","$","`","'","dd","t","f","w","e",";","u","m"]:
    amulet[command] = Amulet(ability_str=command)

# Arquebus - lets you d without moving
arquebus = Item(
    char=")",
    name="arquebus",
    summary="A ranged weapon.",
    ability = SimpleAbility("ranged")
)

# TODO Spellbooks?
