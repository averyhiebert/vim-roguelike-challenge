from __future__ import annotations

from typing import Iterable, Iterator, Optional, TYPE_CHECKING
import re

import numpy as np # type: ignore
import tcod
from tcod.console import Console

from entity import Actor, Item
import tile_types
import colors

from path import Path
from utils import a_or_an
from map_traces import MapTrace

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

        # Used to add fade-out colours.
        # TODO Use proper enum/type
        # For now, format is (x,y,type), where 0 = nothing, 1 = movement
        self.traces:List[MapTrace] = [] 

        # Used for hlsearch highlighting
        self.highlight = np.full((width,height),fill_value=False,order="F")

        # Set of location markers
        self.marks = {}

        # Used as hack for finding nearby chars
        self.console:Optional[Console] = None

    @property
    def items(self) -> Iterator[item]:
        yield from (entity for entity in self.entities 
            if isinstance(entity,Item))

    @property
    def gamemap(self) -> GameMap:
        return self

    @property
    def center(self):
        return (self.width//2, self.height//2)

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over the map's living actors."""
        yield from (e for e in self.entities 
            if isinstance(e,Actor) and e.is_alive)

    def add_trace(self,points:List[Tuple[int,int]],
            color:Tuple[int,int,int]=colors.default_trace) -> None:
        """ Add a trace to draw on the map. Points should be a list
        of (x,y) tuples to add a trace to."""
        self.traces.append(MapTrace(points,fade_time=0.5,color=color))

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

    def get_nearest(self,location:Tuple[int,int],char:str,
            ignore:Option[List[Tuple[int,int]]]=None,
            exclude_adjacent=False) -> List[Tuple[int,int]]:
        """ Return the nearest tile (to the specified location)
        that is rendered as the given char.

        If exclude_adjacent is true, then directly adjacent tiles are not
        considered.
        
        Return None if no valid target found."""
        char_array = self.engine.char_array
        if type(char_array) == type(None):
            raise RuntimeError("Error: console not found (shouldn't happen, knock on wood).")

        location = np.array(location)
        target_val = ord(char)
        candidates = list(zip(*np.nonzero(char_array==target_val)))
        if ignore:
            candidates = [(x,y) for x,y in candidates if (x,y) not in ignore]
        if exclude_adjacent:
            candidates = [c for c in candidates if np.linalg.norm(location - c) > np.sqrt(2) + 0.0000001]
        candidates.sort(key=lambda c: np.linalg.norm(location - c))
        return candidates

    def get_blocking_entity_at_location(self,
            location:Tuple[int,int]) -> Optional[Entity]:
        for entity in self.entities:
            if entity.blocks_movement and entity.pos == location:
                return entity
        return None

    def get_actor_at_location(self,
            location:Tuple[int,int]) -> Optional[Actor]:
        for actor in self.actors:
            if actor.pos == location:
                return actor
        return None

    def get_entities_at_location(self,
            location:Tuple[int,int],sort=False) -> List[Entity]:
        """ Return list of entities at a location.  Can optionally
        also sort them in render order (highest order last)."""
        entities = [e for e in self.entities if e.pos == location]
        if sort:
            entities.sort(key=lambda x: x.render_order.value)
        return entities

    def in_bounds(self, position:Tuple[int,int]) -> bool:
        """ Return true if position is in bounds. """
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height

    def make_mark(self,register:str,position:Tuple[int,int]) -> None:
        if re.match("[a-z]",register):
            self.marks[register] = position
            print(f"Set mark {register}")
        else:
            print("Invalid register")
            # TODO VERY IMPORTANT: This needs to do something better (show
            #  error message to user), currently it just doesn't.
            raise NotImplementedError("TODO: Replace with user error message")

    def get_mark(self,register:str) -> Optional[Tuple[int,int]]:
        """" Return the position associated with the given
        mark (if it exists)."""
        if register in self.marks:
            return self.marks[register]
        else:
            return None

    def get_mono_path(self,start:Tuple[int,int],end:Tuple[int,int]) -> Path:
        """ Returns the straight-line path from a given start point to
        a single end point."""
        points = [(x,y) for x,y in tcod.los.bresenham(start,end)]
        return Path(points=points,game_map=self)

    def get_poly_path(self,points:List[Tuple[int,int]]) -> Path:
        """ Returns the path joining the points given."""
        full_path = []
        for p1,p2 in zip(points[:-1],points[1:]):
            full_path.extend([(x,y) for x,y in tcod.los.bresenham(p1,p2)])
        # Remove duplicates
        full_path = list(dict.fromkeys(full_path))
        return Path(points=full_path,game_map=self)

    def regex_search(self,regex:str) -> List[Tuple[int,int]]:
        """Return a list of locations whose description matches the given
        regex.

        Note: currently uses python regex, not vim regex.
        """
        if regex == "":
            return []
        w,h = self.tiles.shape
        locations = [pos for pos in np.ndindex(self.tiles.shape)
            if re.search(regex,self.describe_tile(pos,visible_only=False))]
        # TODO Text describing # of matches found, etc.
        return locations

    def set_highlight(self,points:List[Tuple[int,int]]) -> None:
        """ Update own highlighting mask (presumably after a regex search)."""
        self.highlight[:,:] = False
        # TODO Vectorize properly
        for point in points:
            self.highlight[point] = True

    def describe_tile(self,location:Tuple[int,int],visible_only=True) -> str:
        """ Return a text description for the given square.

        e.g. "a nano, an ed corpse, floor"

        To be used for regex search and "observe" action. "Observe" action
        should use flag visible_only (i.e. only describe what's visible to
        the player), while regex search should also reveal invisible stuff.
        """
        # TODO Maybe iterating through each entity for each position
        #  is inefficient; could keep some sort of better data structure
        #  if it turns out to be an issue.
        #  I doubt it'll be an issue, though.

        # Helper
        def tile_full_summary(location):
            ind = self.tiles[location]["name_index"]
            tile_name = tile_types.tile_names[ind]

            entities = self.get_entities_at_location(location,sort=True)
            text = ", ".join([f"{a_or_an(e.name)}" 
                for e in reversed(entities)])
            if len(text) > 0:
                text += f", {tile_name}"
            else:
                text = tile_name
            return text

        if visible_only:
            if not self.explored[location]:
                return "unexplored"
            elif not self.visible[location]:
                return tile_types.tile_names[self.tiles[location]["name_index"]]
            else:
                return tile_full_summary(location)
        else:
            return tile_full_summary(location)

    def render(self,console: Console) -> None:
        """ Render the map.

        Draw "visible" tiles using "light" colors,
        explored-but-unseen tiles in "dark" colors,
        and otherwise use "unseen" colors.
        """
        console.tiles_rgb[0:self.width,0:self.height] = np.select(
            condlist=[self.visible,self.explored],
            choicelist=[self.tiles["light"],self.tiles["dark"]],
            default=self.tiles["unseen"]
        )


        # Render highlights
        console.bg[:self.width,:self.height][self.highlight & self.visible] = colors.highlight 
        invisible_highlights = self.highlight & np.logical_not(self.visible)
        console.bg[:self.width,:self.height][invisible_highlights] = colors.highlight_dark
        console.fg[:self.width,:self.height][invisible_highlights] = colors.highlight_dark

        # Draw map traces
        # TODO Make this more vectorized, somehow
        for trace in self.traces:
            for point in trace.points:
                color = trace.get_color(console.bg[point])
                console.bg[point] = color
        # Remove expired traces
        self.traces = [t for t in self.traces if not t.expired]
    
        # Render entities (in correct order)
        entities_sorted_for_rendering = sorted(
            self.entities, key=lambda x: x.render_order.value
        )
        for entity in entities_sorted_for_rendering:
            # Only print entities that are in the FOV
            if self.visible[entity.pos]:
                console.print(x=entity.x,y=entity.y,
                    string=entity.char,fg=entity.color)
            else:
                # Technically, I do print invisible entites, I just print
                #  them in black on black. (This means they are stil t/f-able)
                r,g,b = console.bg[entity.x,entity.y]
                bg = (r,g,b) # Converting np to tuple
                console.print(x=entity.x,y=entity.y,string=entity.char,fg=bg)

        self.console = console # (somewhat) sorry about this
