from __future__ import annotations

from typing import TYPE_CHECKING, Tuple, Union

from game_map import GameMap
import level_factories as lf
import entity_factories as ef
from procgen import sample_from_dist

if TYPE_CHECKING:
    from engine import Engine

level_chances: Dict[int,List[Tuple[Union[Entity,ef.Family]]]] = {
  0:[(lf.default,100)],
  3:[(lf.tunnels,10)],
  5:[(lf.mines,100),(lf.tunnels,100),(lf.default,0)],
  8:[(lf.default,100),
     (lf.bigrooms,50),
     (lf.tunnels,10),
     (lf.mines,10)], # TODO Vault landmines
  11:[(lf.bigrooms,0),
      (lf.great_hall,100),
      (lf.cellar,100),
      (lf.cellar_vertical,100),
      (lf.default,0),
      (lf.tunnels,0),
      (lf.mines,0)],
  13:[(lf.great_hall,0),
      (lf.cellar,0),
      (lf.cellar_vertical,0),
      (lf.disconnected,100)]# TODO Final level?
}

class GameWorld:
    """ Holds a list of game maps and generates new ones, etc."""
    def __init__(
            self,*,engine:Engine,
            map_width:int,
            map_height:int,
            current_floor:int=-1,
            max_floors:int=13,
            tutorial=False):
        self.engine = engine
        self.map_width = map_width
        self.map_height = map_height
        self.current_floor = current_floor
        self.max_floors = max_floors

        # TODO Might eventually keep list of floors, but going back up is
        #  low priority at the moment, seeing as time is running out and I
        #  need most of the last day for UI/polish, rather than new features.
        self.floors = []

        # For the special case of the tutorial level:
        self.tutorial = tutorial

    @property
    def progress_summary(self) -> None:
        """ Return a vim-style summary of progress through the level,
        e.g. Top, Bottom, or a percentage."""
        if self.current_floor == 0:
            return "Top"
        elif self.current_floor == self.max_floors:
            return "Bottom"
        elif self.current_floor > self.max_floors:
            return "??????"
        else:
            percentage = int(100*(self.current_floor/self.max_floors))
            return f"{percentage:d}%"
    
    def generate_floor(self,level:int) -> GameMap:
        """ Generate a floor, according to the distribution of floor types."""
        # TODO Distribution of level types
        if self.tutorial:
            level_type = lf.tutorial
        else:
            level_type = sample_from_dist(level_chances,k=1,
                difficulty=self.current_floor)[0]

        do_stairs = (self.current_floor != 0)
        return level_type.generate((self.map_width,self.map_height),
            self.engine,difficulty=self.current_floor,upstairs=do_stairs)

    def next_floor(self) -> None:
        self.current_floor += 1
        
        if self.current_floor >= len(self.floors):
            new_floor = self.generate_floor(level=self.current_floor)
            self.floors.append(new_floor)
            if self.current_floor == self.max_floors:
                # TODO Also don't place down stair 
                new_floor.place_randomly(ef.amulet_of_yendor,spawn=True)

        floor = self.floors[self.current_floor]
        self.engine.set_game_map(floor)
        if floor.upstairs_location:
            # Always the case, except at very beginning of game
            self.engine.player.place(floor.upstairs_location,self.engine.game_map)

    def prev_floor(self) -> None:
        if self.current_floor == 0:
            # This shouldn't happen, but just in case...
            raise exceptions.Impossible("You are already on the top floor")
        self.current_floor -= 1
        self.engine.set_game_map(self.floors[self.current_floor])
        self.engine.player.place(self.engine.game_map.downstairs_location,self.engine.game_map)

        

