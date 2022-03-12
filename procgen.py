from __future__ import annotations

import random
from typing import Dict, List, Tuple, Union, Iterator, Any, TYPE_CHECKING

import tcod
import numpy as np #type: ignore

import entity_factories as ef
from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

# Item distribution ======================================================

# Define weights for items/item families, difficulty-dependant
# Heuristic: 100 is "typical" weight, so 50 is half as common etc.
# TODO: Make a distribution of individual commands, rather than amulets,
#  so that it can be re-used for spellbooks, scrolls, etc.

# TODO Should be based on item-assigned "rarity" or "value," rather than
#  these vague classes
item_chances: Dict[int,List[Tuple[Union[Entity,ef.Family],int]]] = {
  0: [(ef.moderate_item,100),
      (ef.good_item,20),
     ],
  2: [(ef.good_item,50)],
  5: [(ef.good_item,100),
      (ef.great_item,30),
     ],
  7: [(ef.great_item,50),
      (ef.moderate_item,50)
     ],
  10: [(ef.amazing_item,50),
     ],
}

enemy_chances: Dict[int,List[Tuple[Union[Entity,ef.Family]]]] = {
  0:[(ef.nano,100)],
  1:[(ef.ed,100)],
  2:[(ef.sed,100),(ef.ed,50)],
  3:[(ef.gedit,100),(ef.ed,10),(ef.nano,10)],
  4:[(ef.needle,50),(ef.vimic,5)],
  5:[(ef.needle,100)],
  6:[(ef.vimic,30)],
  8:[(ef.emacs,50),(ef.vimic,50)],
  10:[(ef.vimpire,50)],
  12:[(ef.emax,200)],
}

def sample_from_dist(
        dist:Dict[int,List[Tuple[Union[Any,ef.Family],int]]],
        k:int, difficulty:int) -> List[Any]:
    """ Return k items sampled from the given distribution."""
    weights = {}
    for key, values in dist.items():
        if key > difficulty:
            break
        weights.update({k:v for k,v in values})
    items = list(weights.keys())
    weight_list = list(weights.values())
    return random.choices(items,weights=weight_list,k=k)

# Number of enemies, items, and landmines
enemies_per_level = [
 (0,6),
 (2,7),
 (4,8), # After this point, placing more enemies is probably excessive
]
items_per_level = [
 (0,3),
 (5,4),
]
traps_per_level = [
 (0,0),
 (1,1),
 (3,2),
 (6,3),
 (9,4),
]
landmine_chance_per_level = [
 (0,0),
 (1,0.05),
 (2,0.1),
 (5,0.15),
 (7,0.2)
]

# Helper for interpreting these lists:
def get_level_val(stat_list:List[Tuple[int,int]],level:int):
    val = 0
    for k,v in stat_list:
        if k > level: 
            return val
        else:
            val = v
    return val


# Map generation  ========================================================

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

# Base class for generating levels
class LevelGenerator:
    def __init__(self,name:str):
        self.name=name
        self.difficulty=1 # Should be set by "set difficulty" function at time of generation
        # TODO Either set num_items etc. here, or remove this function from
        #  the class entirely and just pass difficulty in to the various
        #  sub-functions manually.

    def room_mask(self,shape:Tuple[int,int]) -> np.ndarray:
        """ Should return a boolean array that is True for
        walkable tiles and False otherwise.
        
        Using a boolean mask rather than directly returning a gamemap makes
        it easier to isolate the procedural generation into a library that
        could be used for other things, maybe?"""
        raise NotImplementedError()

    def place_items(self,dungeon:GameMap) -> None:
        """ Place items in the dungeon."""
        # TODO possible landmine under item at higher levels?
        num_items = get_level_val(items_per_level,self.difficulty)
        landmine_chance = get_level_val(landmine_chance_per_level,self.difficulty)
        for item in sample_from_dist(item_chances,k=num_items,
            difficulty=self.difficulty):
            if isinstance(item,ef.Family):
                item = item.sample()
            location = dungeon.place_randomly(item,spawn=True)
            if random.random() < landmine_chance:
                ef.landmine.spawn(dungeon,*location)

    def place_enemies(self,dungeon:GameMap) -> None:
        """ Place enemies in the dungeon."""
        # TODO Avoid duplicated code between this and place_items
        #  (Sampling from families should happen in sample_from_dist.)
        num_enemies = get_level_val(enemies_per_level,self.difficulty)
        for enemy in sample_from_dist(enemy_chances,k=num_enemies,
            difficulty=self.difficulty):
            if isinstance(enemy,ef.Family):
                enemy = enemy.sample()
            dungeon.place_randomly(enemy,spawn=True,
                stay_away_center=dungeon.engine.player.pos,
                stay_away_radius=9)

    def place_traps(self,dungeon:GameMap) -> None: 
        num_traps = get_level_val(traps_per_level,self.difficulty)
        for i in range(num_traps):
            dungeon.place_randomly(ef.landmine,spawn=True)


    def place_player(self,dungeon:GameMap,upstairs:bool=True) -> None:
        dungeon.place_randomly(dungeon.engine.player,spawn=False)
        if upstairs:
            location = dungeon.engine.player.pos
            dungeon.upstairs_location = location
            dungeon.tiles[location] = tile_types.up_stairs
        elif self.difficulty == 0:
            # Top level, place a victory altar
            location = dungeon.engine.player.pos
            ef.altar.spawn(dungeon,*location)

    def place_stairs(self,dungeon:GameMap) -> None:
        location = dungeon.get_random_navigable(dungeon.engine.player,
                stay_away_center=dungeon.engine.player.pos,
                stay_away_radius=15)
        dungeon.downstairs_location = location
        dungeon.tiles[location] = tile_types.down_stairs

    def generate(self,shape:Tuple[int,int],
            engine:Engine,difficulty:int,upstairs:bool=True) -> GameMap:
        map_width, map_height = shape
        # Set difficulty first, as other functions may use it
        self.difficulty = difficulty

        player = engine.player
        dungeon = GameMap(engine,map_width, map_height,entities=[player],
            name=f"{self.name} (L{self.difficulty})")
        mask = self.room_mask(shape)
        dungeon.tiles[mask] = tile_types.floor # Set floor based on mask
        
        # Place player first, so that we can (maybe) ensure you don't start
        #  right next to monsters or the exit.
        self.place_player(dungeon,upstairs=upstairs)
        self.place_stairs(dungeon)
        self.place_items(dungeon)
        self.place_enemies(dungeon)
        self.place_traps(dungeon)

        return dungeon

class BasicDungeon(LevelGenerator):
    rooms:List[RectangularRoom]

    def __init__(self,*args,
            room_size_range:Tuple[int,int,int,int]=((8,12),(8,12)),  # min_w, max_w, min_h, max_h,
            max_rooms:int=20,
            diagonal=False,
            invert=False,
            do_tunnels=True,
            allow_overlap=False):
        super().__init__(*args)
        self.room_size_range=room_size_range
        self.max_rooms=max_rooms
        # TODO Later, will set the following based on difficulty
        self.num_items_range=(2,4)
        self.num_enemies_range=(2,4)
        self.allow_overlap = allow_overlap
        self.diagonal = diagonal # Whether to generate diagonal tunnels
        self.invert = invert # Invert floor and all
        self.do_tunnels = do_tunnels

    def room_mask(self,shape) -> np.ndarray:
        """ Should return a boolean array that is True for
        walkable tiles and False otherwise."""
        map_width,map_height = shape
        mask = np.full(shape,False)

        # Add some rooms
        rooms = []
        for r in range(self.max_rooms):
            (min_w,max_w),(min_h,max_h) = self.room_size_range
            room_width = random.randint(min_w,max_w)
            room_height = random.randint(min_h,max_h)
            x = random.randint(0,map_width - room_width - 1)
            y = random.randint(0,map_height - room_height - 1)
            
            new_room = RectangularRoom(x,y,room_width,room_height)
            if not self.allow_overlap:
                if any(new_room.intersects(other_room) for other_room in rooms):
                    continue
            mask[new_room.inner] = True

            if len(rooms) > 0:
                if self.do_tunnels:
                    # Dig tunnel to previous room.
                    for x,y in tunnel_between(rooms[-1].center,new_room.center,
                            diagonal=self.diagonal):
                        mask[x,y] = True
            rooms.append(new_room)
        self.rooms = rooms
        if self.invert:
            mask = np.logical_not(mask)
        return mask


class TestDungeon(LevelGenerator):
    """ A manually created dungeon, for testing."""
    def generate(self,shape:Tuple[int,int],engine:Engine,
            difficulty:int):
        map_width,map_height = shape

        player = engine.player
        dungeon = GameMap(engine,map_width, map_height,entities=[player])
        player.place((40,26),dungeon)

        ef.nano.spawn(dungeon,29,19)
        ef.ed.spawn(dungeon,28,19)
        ef.gedit.spawn(dungeon,29,21)
        #ef.sed.spawn(dungeon,28,20)
        #ef.needle.spawn(dungeon,28,20)
        #ef.vimic.spawn(dungeon,28,20)
        #ef.vimpire.spawn(dungeon,28,20)
        #ef.emacs.spawn(dungeon,28,20)
        #ef.emax.spawn(dungeon,28,20)


        ef.amulet_of_yendor.spawn(dungeon,39,24)
        ef.magnet.spawn(dungeon,38,22)
        ef.scrolls[1].spawn(dungeon,39,23)
        ef.scrolls[2].spawn(dungeon,39,23)
        ef.scrolls[5].spawn(dungeon,39,23)
        ef.scrolls[0].spawn(dungeon,39,23)
        ef.bat_ears.spawn(dungeon,41,20)
        ef.landmine.spawn(dungeon,42,25)
        ef.altar.spawn(dungeon,37,25)

        room_1 = RectangularRoom(x=10,y=10,width=20,height=15)
        room_2 = RectangularRoom(x=35,y=15,width=10,height=15)

        dungeon.tiles[room_1.inner] = tile_types.floor
        dungeon.tiles[room_2.inner] = tile_types.floor
        dungeon.tiles[15:36,18] = tile_types.floor

        return dungeon
