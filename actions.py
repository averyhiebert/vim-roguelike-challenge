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

class MovementAction(Action):
    def __init__(self,dx: int, dy:int):
        super().__init__()
        self.dx = dx
        self.dy = dy

    def perform(self, engine: Engine, entity: Entity) -> None:
        dest = (entity.x + self.dx, entity.y + self.dy)

        if not engine.game_map.in_bounds(*dest):
            return
        if not engine.game_map.tiles["walkable"][dest]:
            return
        entity.move_to(*dest)
