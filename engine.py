from __future__ import annotations

from typing import TYPE_CHECKING
import copy

import tcod
from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

import exceptions
from input_handlers import MainGameEventHandler, CommandEntryEventHandler
from message_log import MessageLog
from status_bar import StatusBar
from text_window import TextWindow
from render_functions import render_stat_box, render_bottom_text

if TYPE_CHECKING:
    from entity import Entity, Actor
    from gamemap import GameMap
    from input_handlers import EventHandler


class Engine:
    game_map: GameMap

    def __init__(self,player:Actor):
        self.player = player
        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.char_array = None # TODO Figure out type
        self.turn = 0 # Turn counter

        # Add some UI elements
        self.top_box_space = 15
        self.status_bar = StatusBar(self)
        self.status_bar.set_long_message("Welcome to the Vim Roguelike Challenge")
        self.text_window = TextWindow(self,
            x=51,y=1 + self.top_box_space,
            width=23, height=38 - 2 - self.top_box_space
        )
        self.message_log = MessageLog(self.text_window)

    def enter_command_mode(self,text:str) -> None:
        self.event_handler = CommandEntryEventHandler(self,text)
        self.status_bar.set_long_message(text)

    def exit_command_mode(self) -> None:
        self.event_handler = MainGameEventHandler(self)
        self.status_bar.set_long_message("")

    def handle_enemy_turns(self) -> None:
        # Reset status message whenever an enemy turn is processed. 
        self.status_bar.reset()

        self.turn += 1
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

        top_box_space = self.top_box_space

        # Render UI stuff
        render_stat_box(console,
            health=self.player.fighter.hp,
            max_health=self.player.fighter.max_hp,
            gold=100
        )
        self.status_bar.render(console)
        self.text_window.render(console)

        context.present(console)
        console.clear()
