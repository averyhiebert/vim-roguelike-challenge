from __future__ import annotations

from typing import TYPE_CHECKING
import copy

import tcod
from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

import exceptions
from input_handlers import MainGameEventHandler
from message_log import MessageLog
from render_functions import render_stat_box

if TYPE_CHECKING:
    from entity import Entity, Actor
    from gamemap import GameMap
    from input_handlers import EventHandler


class Engine:
    game_map: GameMap

    def __init__(self,player:Actor):
        self.player = player
        self.message_log = MessageLog()
        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.char_array = None # TODO Figure out type

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                try:
                    entity.ai.perform()
                except exceptions.Impossible:
                    pass

    def update_fov(self) -> None:
        """ Recompute visible area based on player's POV."""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x,self.player.y),
            radius=10,
            algorithm=tcod.FOV_BASIC,
        )
        self.game_map.explored |= self.game_map.visible
            

    def render(self, console:Console, context:Context):
        self.game_map.render(console)
        # A bit of a hack to enable t/f and possibly w/e movement
        # TODO Update this if I add any offset to the game map
        self.char_array = console.ch[0:self.game_map.width,0:self.game_map.height].copy()

        top_box_space = 15 # Space for stats at top, maybe?

        # Render UI stuff
        self.message_log.render(
            console=console,
            x=self.game_map.width + 1,y=1 + top_box_space,
            width=23, height=self.game_map.height - 2 - top_box_space
        )
        render_stat_box(console,
            health=self.player.fighter.hp,
            max_health=self.player.fighter.max_hp,
            gold=100
        )
        """
        render_bar(
            console=console,
            map_dims=(self.game_map.width,self.game_map.height),
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20
        )
        """

        context.present(console)
        console.clear()
