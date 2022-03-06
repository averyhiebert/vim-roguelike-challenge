from __future__ import annotations

from typing import List, Tuple
from typing import List, Tuple, TYPE_CHECKING

import numpy as np # type: ignore
import tcod

from actions import Action, MeleeAction, MovementAction, WaitAction
from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor

class BaseAI(Action, BaseComponent):
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
    def __init__(self,entity:Actor):
        super().__init__(entity)
        self.path: List[Tuple[int,int]] = []

    def perform(self) -> None:
        target = self.engine.player
        dx, dy = target.x - self.entity.x, target.y - self.entity.y
        distance = max(abs(dx),abs(dy)) #L_infty metric, aka Chebyshev distance

        if self.engine.game_map.visible[self.entity.x,self.entity.y]:
            if distance <= 1:
                return MeleeAction(self.entity,(dx,dy)).perform()
            self.path = self.get_path_to(target.pos)

        if self.path:
            dest_x,dest_y = self.path.pop(0)
            return MovementAction(
                self.entity, 
                (dest_x - self.entity.x, dest_y-self.entity.y),
            ).perform()

        return WaitAction(self.entity).perform()
