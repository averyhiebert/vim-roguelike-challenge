from __future__ import annotations

from typing import List, Any
import random

from components.ai import HostileEnemy, VimlikeEnemy
from components.fighter import Fighter
from components.consumable import HealingConsumable, CommandConsumable
from components.inventory import Inventory
from components.ability import Omnipotent, SimpleAbility, AllCommands
from components.trigger import LandmineTrigger
from entity import Actor, Item, Amulet, Gold
from render_order import RenderOrder
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
    color=colors.player,
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

# Remains stationary until player seen, then tracks indefinitely
nano = Actor(
    char="n",
    color=colors.nano,
    name="nano",
    summary="A harmless text editor.",
    fighter=Fighter(hp=2,AC=0,strength=2,attack_text="bit"),
    ai_cls=HostileEnemy,
    corpse_drop_chance=0.25,
    fov_radius=10,
    needs_los=False,
    wandering=False,
)
# Will follow player by sight if possible, otherwise just wander
ed = Actor(
    char="e",
    color=colors.ed,
    name="ed",
    summary="ed is the standard text editor.",
    fighter=Fighter(hp=4,AC=0,strength=3,attack_text="?"),
    hp_buff=True,
    ai_cls=HostileEnemy,
    fov_radius=11,
    wandering=True,
    needs_los=True,
)
# Same behaviour as ed, but stronger.
sed = Actor(
    char="s",
    color=colors.sed,
    name="sed",
    summary="A feral stream editor.",
    fighter=Fighter(hp=6,AC=0,strength=5,attack_text="s/@/%/"),
    hp_buff=True,
    ai_cls=HostileEnemy,
    fov_radius=11,
    wandering=True,
    needs_los=True,
)
# Same behaviour as nano, but stronger
gedit = Actor(
    char="g",
    color=colors.gedit,
    name="gedit",
    summary="A primitive graphical text editor.",
    fighter=Fighter(hp=6,AC=0,strength=5,attack_text="deleted"),
    ai_cls=HostileEnemy,
    fov_radius=10,
    needs_los=False,
    wandering=False,
)
# Magnetized needle. Wandering, two moves per turn and high attack but low hp.
needle = Actor(
    char="m",
    color=colors.needle,
    name="magnetized needle",
    summary="See xkcd #378",
    fighter=Fighter(hp=4,AC=0,strength=8,attack_text="stabbed"),
    ai_cls=HostileEnemy,
    fov_radius=10,
    needs_los=False,
    wandering=False,
    moves_per_turn=2
)
# Plan: will use dH etc to attack player, or will flee if at less than 1/3 health
# TODO Steal something
vimic = Actor(
    char="v",
    color=colors.vimic,
    name="vimic",
    summary="A monster that mimics the features of vim.",
    fighter=Fighter(hp=15,AC=0,strength=6,attack_text="d"), #TODO dynamic text
    ai_cls=VimlikeEnemy,
    fov_radius=11,
    wandering=True,
    needs_los=True,
    will_flee=True,
)
# Like a vimic, but ranged and moves faster.
# TODO Ability to make you forget an intrinsic command.
vimpire = Actor(
    char="V",
    color=colors.vimpire,
    name="Vimpire",
    summary="A vile, corrupted vim-like entity.",
    fighter=Fighter(hp=20,AC=0,strength=8,attack_text="d"), #TODO dynamic text
    hp_buff=True,
    ai_cls=VimlikeEnemy,
    fov_radius=11,
    wandering=True,
    will_flee=True,
    moves_per_turn=2,
    abilities=[SimpleAbility("ranged")],
    needs_los=True,
)
emacs = Actor(
    char="E",
    color=colors.emacs,
    name="Emacs",
    summary="A lumbering monstrosity created by mad scientists.",
    fighter=Fighter(hp=25,AC=0,strength=10,attack_text="C-x h C-w"), #TODO dynamic text
    hp_buff=True,
    ai_cls=VimlikeEnemy,
    fov_radius=11,
    wandering=True,
    aoe_radius=3,
    can_melee=False,
    abilities=[SimpleAbility("ranged")],
    needs_los=True,
)
emax = Actor(
    char="X",
    color=colors.emacs,
    name="Emax",
    summary="Like Emacs, only moreso.",
    fighter=Fighter(hp=30,AC=0,strength=10,attack_text="C-x h C-w"), #TODO dynamic text
    hp_buff=True,
    ai_cls=VimlikeEnemy,
    fov_radius=11,
    wandering=True,
    aoe_radius=3,
    aoe_cross=True,
    can_melee=False,
    abilities=[SimpleAbility("ranged")],
    needs_los=True,
)

# Traps =========================================================

landmine = Item(
    char=" ",color=colors.default_bg,
    name="landmine",
    summary="Explodes when you step off it.",
    trigger=LandmineTrigger(),
)
landmine.render_order = RenderOrder.TRAP

# Items =========================================================


# Amulets ============
amulet = {}
for command in ["h","j","k","l","H","M","L","0","$","`","'","dd","t","f","w","e",";","u","m"]:
    amulet[command] = Amulet(ability_str=command)
# Special!
amulet_of_yendor = Item(
    char='"',name="Amulet of Yendor",
    color=colors.amulet,
    summary="A powerful and mysterious artifact.",
    ability=AllCommands(),
)

# Scrolls =============
#  (a list, since it's not convenient to type out entire names)
scrolls = []
scroll_commands = [
    ":set hlsearch",
    r":%s/\a//g",    # (note the %s)
    r":%s/\a/%/g",   #
    r":s/\a//g",     # Eliminate all enemies in fov (no corpse)
    r":s/\a/%/g",    # Kill all enemies in fov (+ corpse)
    r':s/["?]/$/g', # Convert visible dropped items into gold
]
for c in scroll_commands:
    scrolls.append(Item(
        name=f"scroll of {c}",
        summary=f"Single-use scroll that performs the command {c}",
        char="?",
        color=colors.scroll,
        consumable=CommandConsumable(c)
    ))
scroll_family = Family(scrolls)

# Bat ears: lets you t/f/w/e outside of fov
# TODO Actually implement this.
bat_ears = Item(
    char="(",name="bat ears",
    color=colors.equipment,
    summary="When equipped, gives you the power of echolocation.",
    ability=SimpleAbility("echolocate")
)
# Arquebus - a ranged item
arquebus = Item(
    char=")",
    name="arquebus",
    summary="A ranged weapon.",
    ability=SimpleAbility("ranged")
)

# Families of items

weak_amulet = Family([amulet[s] for s in "hjkl"])
moderate_item = Family(scrolls[3:] + [amulet[s] for s in "tw;m'`"] 
    + [Gold(1),Gold(2),Gold(4),Gold(3)])
good_item = Family([amulet[s] for s in "feHML0$"] + scrolls[1:3]
    + [Gold(8),Gold(9),Gold(10),Gold(11)])
great_item = Family([amulet["dd"],amulet["u"],arquebus,scrolls[0],bat_ears,Gold(30)])

# TODO Spellbooks?
