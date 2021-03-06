from __future__ import annotations

from typing import List, Tuple
from typing import List, Tuple, TYPE_CHECKING
import math
import random

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
import utils

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

class Inanimate(BaseAI):
    def perform(self) -> None:
        return None

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
            elif euclidean_distance <= self.entity.fov_radius + 0.00001:
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

        Note: returns an action, but does not perform it!
        """
        path_endpoint = None

        directions = {
            "0":(0,self.entity.y),
            "L":(self.entity.x,1000),
            "H":(self.entity.x,0),
            "$":(1000,self.entity.y),
        }
        flee = False # Whether to flee.
        dest:Optional[Tuple[int,int]] = None  # Direction to possibly move to.
        if self.entity.fighter.hp > self.entity.fighter.max_hp/4 or not self.entity.will_flee:
            if self.entity.aoe_radius:
                dx, dy = target.x - self.entity.x, target.y - self.entity.y
                distance = max(abs(dx),abs(dy)) #Chebyshev distance
                if distance <= self.entity.aoe_radius - 1:
                    # Perform aoe attack
                    points = list(utils.aoe_by_radius(self.entity.pos,self.entity.aoe_radius))
                    if self.entity.aoe_cross:
                        # Also add in cross pattern
                        points.pop()
                        w,h = self.entity.gamemap.width,self.entity.gamemap.height
                        points.extend([(x,self.entity.y) for x in range(w)])
                        points.extend([(self.entity.x,y) for y in range(h)])
                        points.extend([self.entity.pos])
                    path = Path(points,game_map=self.entity.gamemap)
                    dest = self.entity.pos
                else:
                    return None # Just move towards player
            else:
                if self.entity.x == target.x:
                    dest = directions["H" if self.entity.y > target.y else "L"]
                elif self.entity.y == target.y:
                    dest = directions["0" if self.entity.x > target.x else "$"]
        else:
            flee = True
            # Run away in random direction orthogonal to player, if in line
            #  of fire, or else just a random direction
            if self.entity.x == target.x:
                dest = directions[random.choice(["0","$"])]
            elif self.entity.y == target.y:
                dest = directions[random.choice(["H","L"])]
            else:
                # TODO Maybe pick the destination which goes furthest from
                #  the player?
                dest = directions[random.choice(["0","$","H","L"])]

        if dest and not flee:
            # Start a d action (takes 2 turns)
            if not self.entity.aoe_radius:
                # Path to chosen direction
                path = self.entity.gamemap.get_mono_path(self.entity.pos,dest)
            else:
                # Actually, instead of a path, just use AOE
                # path is already set?
                pass
            action = ActionDeleteAlongPath(self.entity,path,no_truncate=True)
            self.set_timeout(0,action)
            return WaitAction(self.entity)
        elif dest and flee:
            # Flee immediately
            # Note: does not take 2 turns as this is only one keystroke.
            path = self.entity.gamemap.get_mono_path(self.entity.pos,dest)
            return ActionMoveAlongPath(self.entity,path)
        else:
            # Continue moving towards player
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
            if distance <= 1 and self.entity.can_melee:
                return MeleeAction(self.entity,(dx,dy)).perform()
            elif euclidean_distance <= self.entity.fov_radius:
                # Can see player
                self.target_last_seen = target.pos
                action = self.target_in_view(target)
                if action:
                    return action.perform()
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

