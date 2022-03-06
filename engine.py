from __future__ import annotations

from typing import TYPE_CHECKING
import copy

import tcod
from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

from input_handlers import MainGameEventHandler

if TYPE_CHECKING:
    from entity import Entity, Actor
    from gamemap import GameMap
    from input_handlers import EventHandler


class Engine:
    game_map: GameMap

    def __init__(self,player:Actor):
        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.player = player
        self.char_array = None # TODO Figure out type

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                entity.ai.perform()

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

        # A bit of a hack to enable t/f and possibly w/e movement
        # TODO Update this if I add any offset to the game map
        self.char_array = console.ch[0:self.game_map.width,0:self.game_map.height].copy()

        console.print(x=1,y=self.game_map.height + 1,
            string=f"HP: {self.player.fighter.hp}/{self.player.fighter.max_hp}"
        )

        context.present(console)
        console.clear()
