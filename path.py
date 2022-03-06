from __future__ import annotations

from typing import Tuple, List, TYPE_CHECKING

if TYPE_CHECKING:
    from game_map import GameMap

class Path:
    """ Represents a sequence of squares with a startpoint and an endpoint."""

    def __init__(self,
            points:List[Tuple[int,int]],
            game_map:GameMap):
        self.points = points # List of coordinate pairs
        self.game_map = game_map

    @property
    def start_point(self):
        """ Return starting point of the path. """
        return self.points[0]

    def last_occupiable_square(self,entity:Entity):
        """Returns the last location the given entity can legally occupy.
        
        Throws an error if no such location."""
        i = len(self.points) - 1
        for location in reversed(self.points):
            if self.game_map.is_navigable(location,entity=entity):
                return location
        else:
            raise ValueError("Path must contain at least one valid location.")

    def truncate_to_navigable(self,entity:Entity) -> None:
        """Remove any areas from the path that are beyond the reach of
        the given entity.

        TODO: Make an exception for if the player lands directly on top of
        an enemy (e.g. from w or fe) and thus can't occupy the square, but
        still should be allowed to attack enemy.
        """
        endpoint = self.last_occupiable_square(entity)
        new_points = []
        for location in self.points:
            new_points.append(location)
            if location == endpoint:
                self.points = new_points
                return
        raise RuntimeError("Problem truncating path (this should never happen)")
