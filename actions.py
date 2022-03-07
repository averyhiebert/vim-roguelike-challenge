from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

from utils import roll_dice
import colors

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity

class Action:
    def __init__(self, entity:Actor,skip_turn:bool=False) -> None:
        super().__init__()
        self.entity = entity
        self.skip_turn = skip_turn # True if action does not expend a turn

    @property
    def engine(self) -> Engine:
        """ Return the engine this action belongs to."""
        return self.entity.gamemap.engine

    def perform(self) -> None:
        """ Perform this action with the objects needed to determine
        its scope.

        `self.engine` is the scope the action is being performed in.
        `self.entity` is the one performing the action.

        Must be overridden by subclasses.
        """

        raise NotImplementedError()

class EscapeAction(Action):
    def perform(self) -> None:
        raise SystemExit()

class WaitAction(Action):
    def perform(self) -> None:
        pass

class DummyAction(Action):
    """ An action that does nothing, but can potentially signal that
    no enemy turn is to be performed in response to the latest event.
    
    Currently the same as WaitAction, I guess."""

    def perform(self) -> None:
        pass

class ActionMakeMark(Action):
    """ Make a mark (as in commands m and `)  on the current gamemap."""
    def __init__(self,entity:Entity,register:str):
        super().__init__(entity)
        self.register = register

    def perform(self) -> None:
        self.entity.gamemap.make_mark(self.register,self.entity.pos)
        

class ActionWithPath(Action):
    """ An action that acts along a path of player movement."""
    def __init__(self, entity:Entity, path:Path):
        super().__init__(entity)
        self.path = path

    def perform(self) -> None:
        raise NotImplementedError()

class ActionMoveAlongPath(ActionWithPath):
    """ Move to end of path."""

    def perform(self) -> None:
        self.path.truncate_to_navigable(self.entity)
        destination = self.path.last_occupiable_square(self.entity)
        
        if len(self.path.points) >= 2 and destination == self.path.points[-2]:
            # Possibly a melee attack
            target_x,target_y = self.path.points[-1]
            direction = (target_x - self.entity.x, target_y - self.entity.y)
            # Would be nicer if MeleeAction took a destination, not direction,
            #  but oh well...
            MeleeAction(self.entity,direction).perform()

        self.entity.move_to(*destination)
        if len(self.path.points) > 2:
            self.entity.gamemap.add_trace(self.path.points)

class ActionDeleteAlongPath(ActionWithPath):
    def perform(self) -> None:
        self.path.truncate_to_navigable(self.entity)
        destination = self.path.last_occupiable_square(self.entity)

        # Move (TODO: Maybe this should be optional)
        self.entity.move_to(*destination)

        # Attack everything along path.
        for point in self.path.points:
            target = self.entity.gamemap.get_actor_at_location(point)
            if target and not (target == self.entity):
                target_x,target_y = point
                direction = (target_x - self.entity.x, target_y - self.entity.y)
                MeleeAction(self.entity,direction).perform()
        
        # Draw trace
        if len(self.path.points) > 2:
            self.entity.gamemap.add_trace(self.path.points,
                color=colors.delete_trace)
    
    

class ActionWithDirection(Action):
    def __init__(self, entity:Actor, direction: Tuple[int,int]):
        # Note: action with direction never skips a turn
        super().__init__(entity)
        self.direction = direction

    def perform(self) -> None:
        raise NotImplementedError()

    @property
    def dx(self):
        return self.direction[0]
        
    @property
    def dy(self):
        return self.direction[1]

    @property
    def dest(self):
        """ Returns this action's destination."""
        return (self.entity.x + self.dx, self.entity.y + self.dy)

    @property
    def blocking_entity(self) -> Optional[Entity]:
        """ Return the blocking entity at this action's destination."""
        return self.engine.game_map.get_blocking_entity_at_location(self.dest)

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this action's destination."""
        return self.engine.game_map.get_actor_at_location(self.dest)

class MovementAction(ActionWithDirection):
    def perform(self) -> None:

        if not self.engine.game_map.in_bounds(self.dest):
            return # Destination out of bounds
        if not self.engine.game_map.tiles["walkable"][self.dest]:
            return # Destination blocked by a tile
        if self.blocking_entity:
            return # Destination blocked by entity
        self.entity.move_to(*self.dest)

class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.target_actor

        if not target:
            return # Nothing to attack

        to_hit = roll_dice(self.entity.fighter.to_hit)
        if to_hit > target.fighter.AC:
            damage = roll_dice(self.entity.fighter.damage)
            self.engine.message_log.add_message(
                f"{self.entity.name} attacked {target.name} ({damage} hp)."
            )
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(
                f"{self.entity.name} missed {target.name}."
            )

class BumpAction(ActionWithDirection):
    def perform(self) -> None:

        if self.target_actor:
            return MeleeAction(self.entity,self.direction).perform()
        else:
            return MovementAction(self.entity,self.direction).perform()

