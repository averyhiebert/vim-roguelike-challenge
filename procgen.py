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
item_chances: Dict[int,List[Tuple[Union[Entity,ef.Family],int]]] = {
  0: [(ef.basic_movement_amulet,20), # Boring, so we don't want too many
      (ef.capital_amulet,100),
      (ef.f_amulet,100),
     ],
  3: [(ef.mark_amulet,50),
      (ef.amulet["dd"],30),
      (ef.arquebus,30)
     ],
  4: [(ef.basic_movement_amulet,0), # No point wasting the player's time
      (ef.amulet["u"],30)
     ]
}

enemy_chances: Dict[int,List[Tuple[Union[Entity,ef.Family]]]] = {
  0:[(ef.nano,100)],
  1:[(ef.ed,100)],
  2:[(ef.sed,100),(ef.ed,50)],
  3:[(ef.gedit,100),(ef.ed,10),(ef.nano,10)],
  4:[(ef.needle,50),(ef.vimic,10)],
  5:[(ef.vimic,30)],
  6:[(ef.needle,100)],
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

def place_randomly(dungeon:GameMap,entity:Entity,max_tries=100,
        restricted_range:Optional(Tuple[int,int,int,int])=None,spawn=True):
    """Try up to max_tries times to place the entity somewhere that
    it is allowed to be. Throws an exception otherwise.

    If spawn=True, use the "spawn" function (e.g. for items and enemies).
    Otherwise, place the entity itself (e.g. for the player).

    TODO: I could instead iterate over the valid locations and then pick
    one at random, but in most cases I'm pretty sure this should be faster
    and also reasonably safe.
    """
    # TODO Switch to using GameMap.get_random_navigable
    if not restricted_range:
        restricted_range = (0,dungeon.width-1,0,dungeon.height-1)
    xmin,xmax,ymin,ymax = restricted_range
    for i in range(max_tries):
        location = (random.randint(xmin,xmax),random.randint(ymin,ymax))
        if dungeon.is_navigable(location,entity):
            if spawn:
                entity.spawn(dungeon,*location)
            else:
                entity.place(location,dungeon)
            return
    else:
        # TODO A sensible default.
        raise RuntimeError("Dungeon generation failed.")

# Base class for generating levels
class LevelGenerator:
    def __init__(self,name):
        self.name=name
        self.difficulty=1 # Should be set by "set difficulty" function at time of generation

    def room_mask(self,shape:Tuple[int,int]) -> np.ndarray:
        """ Should return a boolean array that is True for
        walkable tiles and False otherwise.
        
        Using a boolean mask rather than directly returning a gamemap makes
        it easier to isolate the procedural generation into a library that
        could be used for other things, maybe?"""
        raise NotImplementedError()

    def place_items(self,dungeon:GameMap) -> List[Tuple[Item]]:
        """ Place items in the dungeon."""
        # TODO Logic about how many items to sample
        # TODO Optional min distance from player
        num_items = 3
        for item in sample_from_dist(item_chances,k=num_items,
            difficulty=self.difficulty):
            if isinstance(item,ef.Family):
                item = item.sample()
            place_randomly(dungeon,item,max_tries=100)

    def place_enemies(self,dungeon:GameMap) -> List[Tuple[Item]]:
        """ Place enemies in the dungeon."""
        # TODO Avoid duplicated code between this and place_items
        num_enemies = 8
        for enemy in sample_from_dist(enemy_chances,k=num_enemies,
            difficulty=self.difficulty):
            if isinstance(enemy,ef.Family):
                enemy = enemy.sample()
            place_randomly(dungeon,enemy,max_tries=100)

    def place_player(self,dungeon:GameMap) -> None:
        place_randomly(dungeon,dungeon.engine.player,max_tries=100,spawn=False)

    def generate(self,shape:Tuple[int,int],
            engine:Engine,difficulty:int) -> GameMap:
        map_width, map_height = shape
        # Set difficulty first, as other functions may use it
        self.difficulty = difficulty

        player = engine.player
        dungeon = GameMap(engine,map_width, map_height,entities=[player])
        mask = self.room_mask(shape)
        dungeon.tiles[mask] = tile_types.floor # Set floor based on mask
        
        # Place player first, so that we can (maybe) ensure you don't start
        #  right next to monsters or the exit.
        self.place_player(dungeon)
        self.place_items(dungeon)
        self.place_enemies(dungeon)

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

        #ef.nano.spawn(dungeon,29,19)
        #ef.ed.spawn(dungeon,28,19)
        #ef.gedit.spawn(dungeon,29,21)
        #ef.sed.spawn(dungeon,28,20)
        #ef.needle.spawn(dungeon,28,20)
        #ef.vimic.spawn(dungeon,28,20)
        #ef.vimpire.spawn(dungeon,28,20)
        ef.emacs.spawn(dungeon,28,20)
        #ef.emax.spawn(dungeon,28,20)


        ef.amulet_of_yendor.spawn(dungeon,39,24)
        ef.arquebus.spawn(dungeon,39,22)

        room_1 = RectangularRoom(x=10,y=10,width=20,height=15)
        room_2 = RectangularRoom(x=35,y=15,width=10,height=15)

        dungeon.tiles[room_1.inner] = tile_types.floor
        dungeon.tiles[room_2.inner] = tile_types.floor
        dungeon.tiles[15:36,18] = tile_types.floor

        return dungeon
