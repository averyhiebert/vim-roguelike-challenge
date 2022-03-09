from __future__ import annotations

from typing import Tuple

import entity_factories
from game_map import GameMap
import tile_types

class RectangularRoom:
    def __init__(self, x:int, y:int, width:int, height:int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> Tuple[int,int]:
        center_x = (self.x1 + self.x2)//2
        center_y = (self.y1 + self.y2)//2
        return center_x, center_y

    @ property
    def inner(self) -> Tuple[slice,slice]:
        return slice(self.x1+1,self.x2), slice(self.y1+1,self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        """ Return true if this room overlaps with other room. """
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )

def generate_dungeon(map_width:int,map_height:int,engine:Engine) -> GameMap:
    """ Not gonna bother with random generation until I have
    most of the vim commands/movement/etc. dealt with, since
    that's the core priority for this game.
    """

    player = engine.player
    dungeon = GameMap(engine,map_width, map_height,entities=[player])
    player.place((40,26),dungeon)

    entity_factories.nano.spawn(dungeon,25,11)
    entity_factories.nano.spawn(dungeon,29,19)
    entity_factories.ed.spawn(dungeon,28,19)
    entity_factories.nano.spawn(dungeon,16,16)
    entity_factories.ed.spawn(dungeon,16,20)
    entity_factories.ed.spawn(dungeon,18,20)
    entity_factories.ed.spawn(dungeon,27,22)

    entity_factories.amulet["dd"].spawn(dungeon,39,24)
    entity_factories.amulet["H"].spawn(dungeon,39,24)
    entity_factories.amulet["M"].spawn(dungeon,39,24)
    entity_factories.amulet["m"].spawn(dungeon,39,24)
    entity_factories.amulet["`"].spawn(dungeon,39,24)
    entity_factories.arquebus.spawn(dungeon,39,22)

    room_1 = RectangularRoom(x=10,y=10,width=20,height=15)
    room_2 = RectangularRoom(x=35,y=15,width=10,height=15)

    dungeon.tiles[room_1.inner] = tile_types.floor
    dungeon.tiles[room_2.inner] = tile_types.floor
    dungeon.tiles[15:36,18] = tile_types.floor


    return dungeon

