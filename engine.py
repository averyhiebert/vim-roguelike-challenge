from typing import Iterable, Any

import tcod
from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

from entity import Entity
from game_map import GameMap
from input_handlers import EventHandler


class Engine:
    def __init__(self,
            event_handler:EventHandler, 
            game_map: GameMap,
            player:Entity):
        self.event_handler = event_handler
        self.player = player
        self.game_map = game_map
        self.update_fov()

    def handle_enemy_turns(self) -> None:
        for entity in self.game_map.entities - {self.player}:
            print(f"The {entity.name} does nothing")

    def handle_events(self, events: Iterable[Any]) -> None:
        for event in events:
            action = self.event_handler.dispatch(event)

            if not action:
                continue
            action.perform(self, self.player)
            self.handle_enemy_turns()
            self.update_fov() # Update the FOV before player's next action
    
    def update_fov(self) -> None:
        """ Recompute visible area based on player's POV."""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x,self.player.y),
            radius=12,
            algorithm=tcod.FOV_BASIC,
        )
        self.game_map.explored |= self.game_map.visible
            

    def render(self, console:Console, context:Context):
        self.game_map.render(console)

        context.present(console)
        console.clear()
