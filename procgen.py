from __future__ import annotations

from typing import Tuple

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

def generate_dungeon(map_width,map_height) -> GameMap:
    """ Not gonna bother with random generation until I have
    most of the vim commands/movement/etc. dealt with, since
    that's the core priority for this game.
    """
    dungeon = GameMap(map_width, map_height)

    room_1 = RectangularRoom(x=10,y=10,width=20,height=15)
    room_2 = RectangularRoom(x=35,y=15,width=10,height=15)

    dungeon.tiles[room_1.inner] = tile_types.floor
    dungeon.tiles[room_2.inner] = tile_types.floor
    dungeon.tiles[15:36,18] = tile_types.floor

    return dungeon

