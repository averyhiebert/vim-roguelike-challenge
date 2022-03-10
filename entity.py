from __future__ import annotations

import copy
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING, Union

import colors
from render_order import RenderOrder
from utils import a_or_an

from components.consumable import HealingConsumable, NotConsumable
from components.inventory import Inventory
from components.ability import SimpleAbility, AllCommands

import utils

if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.consumable import Consumable
    from components.fighter import Fighter
    from components.inventory import Inventory
    from components.ability import Ability
    from game_map import GameMap
    from engine import Engine

T = TypeVar("T",bound="Entity")

class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    parent: Union[GameMap, Inventory]

    # TODO switch all entities from x/y to single position attribute
    def __init__(self, 
            parent: Optional[GameMap] = None,
            x:int=0, y:int=0, char:str="?", 
            color:Tuple[int,int,int]=(255,255,255),
            name:str="<Unnamed>",
            summary:str="Unknown entity",
            blocks_movement:bool=False,
            render_order:RenderOrder=RenderOrder.CORPSE):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        # Note: name & summary will be used by regex search, if I get there
        self.name = name
        self.summary = summary
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        if parent:
            self.parent = parent
            parent.entities.add(self)

    @property
    def gamemap(self) -> GameMap:
        return self.parent.gamemap

    @property
    def engine(self) -> Engine:
        return self.gamemap.engine

    def enable_all(self) -> None:
        """ Add AllCommands to existing abilities."""
        self.abilities.append(AllCommands())

    def spawn(self: T, gamemap: GameMap, x: int, y:int) -> T:
        """Spawn a copy of this instance at given location."""
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.parent = gamemap
        gamemap.entities.add(clone)
        return clone

    def place(self,location:Tuple[int,int],gamemap:Optional[GameMap]=None) -> None:
        """ Place at new location.  Handles moving across gamemaps."""
        self.x, self.y = location
        if gamemap:
            if hasattr(self,"parent"):
                if self.parent is self.gamemap:
                    self.gamemap.entities.remove(self)
            self.parent = gamemap
            gamemap.entities.add(self)

    def move_to(self,dest_x,dest_y) -> None:
        self.x = dest_x
        self.y = dest_y

    @property
    def pos(self) -> Tuple[int,int]:
        """ The entity's position as a tuple. """
        return (self.x,self.y)

class Actor(Entity):
    def __init__(self,*,x:int=0,y:int=0,char:str="?",
            color:Tuple[int,int,int]=colors.default_fg,
            name:str="<Unnamed>",
            summary:str="An unknown entity.",
            ai_cls:Type[BaseAI], # so we can specify the AI at creation without having to create an instance
            fighter:Fighter,
            max_range:int=0,
            needs_los:bool=True,
            fov_radius:int=1000, # i.e. no limit by default
            hp_buff:bool=False, # Whether corpse should buff hp
            abilities:List[Ability]=[],
            inventory:Optional[Inventory]=None):
        super().__init__(
            x=x,y=y,
            char=char,
            color=color,
            name=name,
            summary=summary,
            blocks_movement=True,
            render_order=RenderOrder.ACTOR,
        )
        self.ai:Optional[BaseAI] = ai_cls(self)
        self.abilities=abilities
        self.fighter = fighter
        self.fighter.parent = self
        if not inventory:
            inventory = Inventory(capacity=0)
        self.inventory = inventory
        self.inventory.parent = self
        self.hp_buff = hp_buff
        self.needs_los = needs_los # Whether this being needs line-of-sight

        # Some stats:
        self.fov_radius = fov_radius
        self.gold=0
        # Max number used in commands (only really relevant to player)
        self.max_range = max_range

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)

    @property
    def ability_string(self) -> str:
        abilities = set([a.ability_string for a in self.abilities])
        abilities.update([item.ability.ability_string
            for item in self.inventory.equipped])
        if "" in abilities:
            # Remove case of non-abilities, e.g. corpses
            abilities.remove("")
        return ", ".join(list(abilities))

    def fulfills(self,requirement:str) -> bool:
        """ Check whether we intrinsically have this ability or
        have it via equipped items in the inventory."""
        for a in self.abilities:
            if a.fulfills(requirement):
                return True
        return self.inventory.fulfills(requirement)

# Note: I will probably change some things about this once I've finished 
#  with the tutorial, but sticking with the tutorial for now until I have
#  a basically working engine to mess with.
class Item(Entity):
    def __init__(self,*,
            x=0,y=0,
            char:str="?",
            color:Tuple[int,int,int]=colors.default_fg,
            name:str="<Unnamed>",
            summary:str="An unknown item.",
            consumable: Optional[Consumable]=None,
            ability:Optional[Ability]=None):
        super().__init__(
            x=x,y=y,char=char,color=color,name=name,
            summary=summary,
            blocks_movement=False,
            render_order=RenderOrder.ITEM
        )
        if not ability:
            ability = SimpleAbility("")
        if not consumable:
            consumable = NotConsumable(f"You can't eat {utils.a_or_an(name)}.")
        # TODO: Set default do-nothing consumable by default
        self.consumable=consumable
        self.consumable.parent = self
        self.ability = ability

    def fulfills(self,req:str) -> bool:
        return self.ability.fulfills(req)

class PassiveAbilityItem(Item):
    def __init__(self,*,
            x=0,y=0,
            char:str="?",
            color:Tuple[int,int,int]=colors.default_fg,
            name:str="<Unnamed>",
            summary:str="An unknown item.",
            ability:Ability):
        super().__init__(
            x=x,y=y,char=char,
            color=color,
            name=name,
            summary=summary
        )
        self.ability = ability

class Amulet(PassiveAbilityItem):
    def __init__(self,*,
            x=0,y=0,
            color:Tuple[int,int,int]=colors.default_fg,
            name:str="<Unnamed>",
            summary:str="An unknown item.",
            ability_str:str):
        name = f"amulet of {ability_str}"
        summary = f"When equipped, you may use the command {ability_str}"
        super().__init__(
            x=x,y=y,char='"',color=color,
            name=name,
            summary=summary,
            ability=SimpleAbility(ability_str)
        )

class Corpse(Item):
    def __init__(self,a:Actor):
        consumable = HealingConsumable(
            int(1.5*a.fighter.strength),
            hp_buff=a.hp_buff
        )
        super().__init__(
            x=a.x,y=a.y,color=a.color,
            char="%",
            name=f"{a.name} corpse",
            summary=f"The remains of {a_or_an(a.name)}.",
            consumable=consumable,
        )
        self.parent = a.parent
        self.render_order=RenderOrder.CORPSE
