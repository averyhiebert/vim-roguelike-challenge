from __future__ import annotations

from typing import TYPE_CHECKING

from game_map import GameMap
import level_factories as lf
import entity_factories as ef
from procgen import sample_from_dist

if TYPE_CHECKING:
    from engine import Engine

class GameWorld:
    """ Holds a list of game maps and generates new ones, etc."""
    def __init__(
            self,*,engine:Engine,
            map_width:int,
            map_height:int,
            current_floor:int=-1,
            max_floors:int=12):
        self.engine = engine
        self.map_width = map_width
        self.map_height = map_height
        self.current_floor = current_floor
        self.max_floors = max_floors

        # TODO Might eventually keep list of floors, but going back up is
        #  low priority at the moment, seeing as time is running out and I
        #  need most of the last day for UI/polish, rather than new features.
        self.floors = []
    
    def generate_floor(self,level:int) -> GameMap:
        """ Generate a floor, according to the distribution of floor types."""
        # TODO Distribution of level types
        do_stairs = (self.current_floor != 0)
        return lf.default.generate((self.map_width,self.map_height),
            self.engine,difficulty=self.current_floor,upstairs=do_stairs)

    def next_floor(self) -> None:
        self.current_floor += 1
        new_floor = self.generate_floor(level=self.current_floor)
        #self.floors.append(new_floor)
        self.engine.set_game_map(new_floor)
        
        if self.current_floor == self.max_floors:
            new_floor.place_randomly(ef.amulet_of_yendor,spawn=True)
        

