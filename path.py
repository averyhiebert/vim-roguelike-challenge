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
    def start(self):
        """ Return starting point of the path. """
        return self.points[0]

    @property
    def end(self):
        """ Return final point on path. """
        return self.points[-1]

    def last_occupiable_square(self,entity:Entity):
        """Returns the last location the given entity can legally occupy.
        
        Throws an error if no such location."""
        i = len(self.points) - 1
        for location in reversed(self.points):
            if self.game_map.is_navigable(location,entity=entity):
                return location
        else:
            # Sometimes occurs when path has length 0, although this really
            #  isn't supposed to happen.
            # Just return current location instead, a reasonably safe fallback
            return entity.pos

    def truncate_to_navigable(self,entity:Entity,
            include_barrier:bool=True) -> None:
        """Remove any areas from the path that are beyond the reach of
        the given entity.

        If include_barrier is True, one additional position on the path
        may also be included (e.g. to attack something that you attempted
        to move on to).
        """
        endpoint = self.last_occupiable_square(entity)
        index = self.points.index(endpoint)
        if include_barrier:
            sliced = self.points[:index+2]
        else:
            sliced = self.points[:index+1]
        self.points = sliced
