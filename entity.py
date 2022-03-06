from __future__ import annotations

import copy
from typing import Optional, Tuple, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from game_map import GameMap

T = TypeVar("T",bound="Entity")

class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    gamemap: GameMap

    # TODO switch all entities from x/y to single position attribute
    def __init__(self, 
            gamemap: Optional[GameMap] = None,
            x:int=0, y:int=0, char:str="?", 
            color:Tuple[int,int,int]=(255,255,255),
            name:str="<Unnamed>",
            summary:str="Unknown entity",
            blocks_movement:bool=False):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        # Note: name & summary will be used by regex search, if I get there
        self.name = name
        self.summary = summary
        self.blocks_movement = blocks_movement
        if gamemap:
            self.gamemap = gamemap
            gamemap.entities.add(self)

    def spawn(self: T, gamemap: GameMap, x: int, y:int) -> T:
        """Spawn a copy of this instance at given location."""
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.gamemap = gamemap
        gamemap.entities.add(clone)
        return clone

    def place(self,location:Tuple[int,int],gamemap:Optional[GameMap]=None) -> None:
        """ Place at new location.  Handles moving across gamemaps."""
        self.x, self.y = location
        if gamemap:
            if hasattr(self,"gamemap"):
                self.gamemap.entities.remove(self)
            self.gamemap = gamemap
            gamemap.entities.add(self)

    def move_to(self,dest_x,dest_y) -> None:
        self.x = dest_x
        self.y = dest_y

    @property
    def pos(self) -> Tuple[int,int]:
        """ The entity's position as a tuple. """
        return (self.x,self.y)

