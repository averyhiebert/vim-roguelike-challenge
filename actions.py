from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

class Action:
    def perform(self, engine:Engine, entity:Entity) -> None:
        """ Perform this action with the objects needed to determine
        its scope.

        `engine` is the scope the action is being performed in.
        `entity` is the one performing the action.

        Must be overridden by subclasses.
        """

        raise NotImplementedError()

class EscapeAction(Action):
    def perform(self, **args) -> None:
        raise SystemExit()

class ActionWithDirection(Action):
    def __init__(self, direction: Tuple[int,int]):
        super().__init__()
        self.direction = direction

    def perform(self, engine:Engine, entity:Entity) -> None:
        raise NotImplementedError()

    @property
    def dx(self):
        return self.direction[0]
        
    @property
    def dy(self):
        return self.direction[1]

class MovementAction(ActionWithDirection):

    def perform(self, engine: Engine, entity: Entity) -> None:
        dest = (entity.x + self.dx, entity.y + self.dy)

        if not engine.game_map.in_bounds(dest):
            return # Destination out of bounds
        if not engine.game_map.tiles["walkable"][dest]:
            return # Destination blocked by a tile
        if engine.game_map.get_blocking_entity_at_location(dest):
            return # Destination blocked by entity
        entity.move_to(*dest)

class MeleeAction(ActionWithDirection):
    def perform(self, engine:Engine, entity:Entity) -> None:
        dest = (entity.x + self.dx, entity.y + self.dy)
        target = engine.game_map.get_blocking_entity_at_location(dest)
        if target:
            print(f"You attacked {target.name}")

class BumpAction(ActionWithDirection):
    def perform(self, engine:Engine, entity:Entity) -> None:
        dest = (entity.x + self.dx, entity.y + self.dy)

        if engine.game_map.get_blocking_entity_at_location(dest):
            return MeleeAction(self.direction).perform(engine,entity)
        else:
            return MovementAction(self.direction).perform(engine,entity)

