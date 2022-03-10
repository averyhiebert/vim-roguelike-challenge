from __future__ import annotations

from typing import Tuple, Iterator, TYPE_CHECKING
import random

import tcod

import entity_factories
from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from entity import Entity

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

def tunnel_between(start:Tuple[int,int],
        end:Tuple[int,int],diagonal=False) -> Iterator[Tuple[int,int]]:
    """ Give a path between two rooms, either L-shaped, or stright-line,
    depending on `diagonal`.
    """
    (x1,y1),(x2,y2) = start,end
    if diagonal:
        yield from tcod.los.bresenham(start,end)
        yield from tcod.los.bresenham((x1+1,y1),(x2+1,y2))
    else:
        corner = (x2,y1) if random.random() < 0.5 else (x1,y2)
        yield from tcod.los.bresenham(start,corner)
        yield from tcod.los.bresenham(corner,end)

def generate_dungeon(
        map_width:int,
        map_height:int,
        engine:Engine,
        room_size_range:Tuple[int,int,int,int],  # min_w, max_w, min_h, max_h,
        num_items_range:Tuple[int,int],  # min_items, max_items
    ) -> GameMap:
    """
    Generate a very generic dungeon
    (rectangular rooms connected by paths).
    """
    player = engine.player
    dungeon = GameMap(engine,map_width, map_height,entities=[player])
    player.place((40,26),dungeon)

    # Add some rooms
    room_1 = RectangularRoom(x=10,y=10,width=12,height=15)
    room_2 = RectangularRoom(x=35,y=15,width=10,height=15)
    dungeon.tiles[room_1.inner] = tile_types.floor
    dungeon.tiles[room_2.inner] = tile_types.floor
    for x,y in tunnel_between(room_1.center,room_2.center,diagonal=False):
        dungeon.tiles[x,y] = tile_types.floor

    # Connect with corridors

    # Add some items

    # Add some monsters
    return dungeon

def test_dungeon(map_width:int,map_height:int,engine:Engine) -> GameMap:
    """
    A manually created dungeon, for testing.
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

