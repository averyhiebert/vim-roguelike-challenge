from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

class Action:
    def __init__(self, entity:Entity) -> None:
        super().__init__()
        self.entity = entity

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

class ActionWithDirection(Action):
    def __init__(self, entity:Entity, direction: Tuple[int,int]):
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
        target = self.blocking_entity
        if target:
            print(f"You attacked {target.name}")

class BumpAction(ActionWithDirection):
    def perform(self) -> None:

        if self.blocking_entity:
            return MeleeAction(self.entity,self.direction).perform()
        else:
            return MovementAction(self.entity,self.direction).perform()

