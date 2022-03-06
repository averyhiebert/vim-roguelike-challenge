from __future__ import annotations

from typing import Iterable, TYPE_CHECKING

import numpy as np # type: ignore
import tcod
from tcod.console import Console

import tile_types

from path import Path

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

class GameMap:
    def __init__(self, engine:Engine,
            width:int, height: int,
            entities: Iterable[Entity] = ()):
        self.engine = engine
        self.width, self.height = width, height
        self.entities = set(entities)
        self.tiles = np.full((width,height),
            fill_value=tile_types.wall,order="F")

        # Can currently see:
        self.visible = np.full((width,height),fill_value=False,order="F")
        # Have been seen before:
        self.explored = np.full((width,height),fill_value=False,order="F")

    def is_navigable(self,location:Tuple[int,int],
            entity:Entity=None) -> Optional[Entity]:
        """ Return true if given entity (usually the player)
        can legally occupy this tile."""
        if not entity:
            # Can't use "self" in default param, apparently
            entity = self.engine.player
        if not self.in_bounds(location):
            return False
        if not self.tiles["walkable"][location]:
            return False
        blocking = self.get_blocking_entity_at_location(location)
        if blocking and blocking != entity:
            # Note: entity does not block self.
            return False
        return True

    def get_blocking_entity_at_location(self,
            location:Tuple[int,int]) -> Optional[Entity]:
        for entity in self.entities:
            if entity.blocks_movement and entity.pos == location:
                return entity
        return None

    def in_bounds(self, position:Tuple[int,int]) -> bool:
        """ Return true if position is in bounds. """
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height

    def get_mono_path(self,start:Tuple[int,int],end:Tuple[int,int]) -> Path:
        """ Returns the straight-line path from a given start point to
        a single end point."""
        points = [(x,y) for x,y in tcod.los.bresenham(start,end)]
        return Path(points=points,game_map=self)

    def render(self,console: Console) -> None:
        """ Render the map.

        Draw "visible" tiles using "light" colors,
        explored-but-unseen tiles in "dark" colors,
        and otherwise use "unseen" colors.
        """
        #console.tiles_rgb[0:self.width,0:self.height] = self.tiles["dark"]
        console.tiles_rgb[0:self.width,0:self.height] = np.select(
            condlist=[self.visible,self.explored],
            choicelist=[self.tiles["light"],self.tiles["dark"]],
            default=self.tiles["unseen"]
        )

        for entity in self.entities:
            # Only print entities that are in the FOV
            if self.visible[entity.pos]:
                console.print(x=entity.x,y=entity.y,string=entity.char,fg=entity.color)
