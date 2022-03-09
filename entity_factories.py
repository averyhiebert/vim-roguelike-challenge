from components.ai import HostileEnemy
from components.fighter import Fighter
from components.consumable import HealingConsumable
from components.inventory import Inventory
from entity import Actor, Item, Amulet
import colors

player = Actor(
    char="@",
    color=colors.default_fg,
    name="player",
    summary="A daring rogue.",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=30,AC=10,to_hit="1d20",damage="1d20"),
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

# Define items here
health_potion = Item(
    char="?",
    name="health potion",
    summary="A potion that restores health.",
    consumable=HealingConsumable(4),
)

# Dictionary of amulet items
amulet = {}
for command in ["h","j","k","l","H","M","L","0","$","`","'","dd","t","f","w","e",";","u","m"]:
    amulet[command] = Amulet(ability_str=command)
