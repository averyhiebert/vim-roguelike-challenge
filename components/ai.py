from __future__ import annotations

from typing import List, Tuple
from typing import List, Tuple, TYPE_CHECKING
import math

import numpy as np # type: ignore
import tcod

from actions import Action, MeleeAction, MovementAction, WaitAction

if TYPE_CHECKING:
    from entity import Actor

class BaseAI(Action):
    entity:Actor

    def perform(self) -> None:
        raise NotImplementedError()

    def get_path_to(self,dest:Tuple[int,int]) -> List[Tuple[int,int]]:
        """ Compute and return a path to the target position."""
        cost = np.array(self.entity.gamemap.tiles["walkable"],dtype=np.int8)
        # Check for blocking entities
        for entity in self.entity.gamemap.entities:
            if entity.blocks_movement and cost[entity.pos]:
                cost[entity.pos] += 10

        # Create graph
        graph = tcod.path.SimpleGraph(cost=cost,cardinal=2,diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.x,self.entity.y)) # start position
        
        path: List[List[int]] = pathfinder.path_to(dest)[1:].tolist()
        return [(x,y) for x,y in path]

class HostileEnemy(BaseAI):
    def __init__(self,entity:Actor,needs_los:bool=True):
        super().__init__(entity)
        self.target_last_seen:Optional[Tuple[int,int]] = None
        self.path: List[Tuple[int,int]] = []
        self.currently_wandering = True


    def perform(self) -> None:
        target = self.engine.player
        dx, dy = target.x - self.entity.x, target.y - self.entity.y
        distance = max(abs(dx),abs(dy)) #L_infty metric, aka Chebyshev distance
        euclidean_distance = math.sqrt(dx**2 + dy**2)

        # Some notes:
        # Always need line-of-sight to be "activated," but some enemies
        # will persist in tracking once activated, even when they no longer
        # see the player.

        if self.engine.game_map.visible[self.entity.x,self.entity.y]:
            # Is in fov of player, but maybe not of self
            if distance <= 1:
                return MeleeAction(self.entity,(dx,dy)).perform()
            elif euclidean_distance <= self.entity.fov_radius:
                # Can see player
                self.target_last_seen = target.pos
        elif self.target_last_seen and not self.entity.needs_los:
                # Can't "see" player, but don't need to.
                #  We can smell them, I guess.
                self.target_last_seen = target.pos

        if self.target_last_seen:
            self.currently_wandering = False
            # We may or may not see the player, but we at least know
            #  where we last saw them
            if self.target_last_seen != self.entity.pos:
                self.path = self.get_path_to(self.target_last_seen)
            else:
                # They're not here, give up
                self.target_last_seen = None
                self.currently_wandering = True
                self.path = None
        else:
            self.currently_wandering = True
        
        # Possibly wander around
        if self.entity.wandering and not self.path:
            location = self.entity.gamemap.get_random_navigable(self.entity)
            self.path = self.get_path_to(location)

        if self.path:
            if self.currently_wandering and self.entity.engine.turn % 2 == 0:
                return WaitAction(self.entity).perform()
            dest_x,dest_y = self.path.pop(0)
            return MovementAction(
                self.entity, 
                (dest_x - self.entity.x, dest_y-self.entity.y),
            ).perform()

        return WaitAction(self.entity).perform()
