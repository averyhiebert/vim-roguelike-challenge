from __future__ import annotations

from typing import List, Tuple
from typing import List, Tuple, TYPE_CHECKING
import math

import numpy as np # type: ignore
import tcod

from actions import (
    Action,
    MeleeAction,
    MovementAction,
    WaitAction,
    ActionDeleteAlongPath,
    ActionMoveAlongPath
)
from path import Path

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
    def __init__(self,entity:Actor):
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

class VimlikeEnemy(HostileEnemy):
    """ An enemy with some abilities similar to the player."""
    def __init__(self,entity:Actor):
        super().__init__(entity)
        # Stuff for taking multi-turn actions
        self.timeout_remaining:int = 0
        self.timeout_action:Optional[Action] = None

    def set_timeout(self,turns:int,action:Action) -> None:
        """ Set a timer to complete the specified action in the specified
        number of turns."""
        self.timeout_remaining = turns
        self.timeout_action = action

    def target_in_view(self,target:Actor) -> Optional[Action]:
        """Either returns some sort of action, or none; in the latter
        case, continue with the rest of the AI logic.
        
        Decides what to do in cases where the player is in view.

        For now, we attack if possible, but may add additional
         features (e.g. running away, or special AOE attack for Emacs)
        """
        # TODO Implement
        path_endpoint = None
        if self.entity.x == target.x:
            if self.entity.y > target.y:
                path_endpoint = (self.entity.x,0)
            else:
                path_endpoint = (self.entity.x,1000) # i.e. all the way down
        elif self.entity.y == target.y:
            if self.entity.x > target.x:
                path_endpoint = (0, self.entity.y)
            else:
                path_endpoint = (10000, self.entity.y) # i.e. all the way right
        if path_endpoint:
            # Start a d action (takes 2 turns)
            path = self.entity.gamemap.get_mono_path(self.entity.pos,
                path_endpoint)
            action = ActionDeleteAlongPath(self.entity,path)
            self.set_timeout(1,action)
            return WaitAction(self.entity).perform()
        else:
            return None

    def perform(self) -> None:
        if self.timeout_remaining > 0:
            # Performing a multi-stage action.
            self.timeout_remaining -= 1
            return WaitAction(self.entity).perform()
        elif self.timeout_remaining == 0 and self.timeout_action:
            action = self.timeout_action
            self.timeout_action = None
            return action.perform()

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
                action = self.target_in_view(target)
                if action:
                    return action
                else:
                    # Nothing in particular needs to happen here
                    pass
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

