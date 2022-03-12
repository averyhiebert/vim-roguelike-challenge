from __future__ import annotations

from typing import TYPE_CHECKING
import copy

import lzma
import pickle

import tcod
from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

import exceptions
from input_handlers import (
    MainGameEventHandler,
    CommandEntryEventHandler,
    CursorMovementEventHandler,
)
from message_log import MessageLog
from status_bar import StatusBar
from text_window import TextWindow
from render_functions import render_stat_box, render_cursor

if TYPE_CHECKING:
    from entity import Entity, Actor
    from gamemap import GameMap
    from game_world import GameWorld
    from input_handlers import EventHandler


class Engine:
    game_map: GameMap
    game_world: GameWorld

    def __init__(self,player:Actor):
        self.player = player
        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.char_array = None # TODO Figure out type
        self.turn = 0 # Turn counter
        self.last_save = -1


        # Add some UI elements
        self.top_box_space = 15
        self.status_bar = StatusBar(self)
        self.status_bar.set_long_message("New game started.")
        self.text_window = TextWindow(self,
            x=51,y=1 + self.top_box_space,
            width=23, height=38 - 2 - self.top_box_space
        )
        self.message_log = MessageLog(self.text_window)

        # Cursor stuff
        # Cursor is a copy of player, but does nothing except move.
        #  (i.e. not in entities list, so other functions won't find it.)
        # TODO Handle this better (bit of a hack currently)
        self.cursor_entity = copy.deepcopy(self.player)
        self.show_cursor=False

        # Global settings
        self.hlsearch = False
        # Render invisible, i.e. will tf work outside of fov:
        self.include_invisible_characters = False

    @property
    def coords_to_show(self) -> Tuple[int,int]:
        """ Coords to show in the status bar."""
        if self.show_cursor:
            return self.cursor
        else:
            return self.player.pos

    @property
    def cursor(self) -> Tuple[int,int]:
        """ Return cursor coordinates."""
        return self.cursor_entity.pos

    def save_as(self,fname:str="save.sav") -> None:
        """ Save self to file.

        Using pickles is not ideal long-term (versioning issues etc), but
         for a 7-day challenge this is good enough!
        """
        save_data = lzma.compress(pickle.dumps(self))
        with open(fname, "wb") as f:
            f.write(save_data)
        self.last_save = self.turn

    @classmethod
    def load(cls,fname:str) -> None:
        with open(fname,"rb") as f:
            engine=pickle.loads(lzma.decompress(f.read()))
        assert isinstance(engine,cls)
        return engine

    def set_game_map(self,game_map:GameMap) -> None:
        self.game_map = game_map
        #if not self.player.gamemap == self.game_map:
        #    self.player.place(game_map.upstairs_location,game_map)
        self.cursor_entity.parent = self.game_map

    def show_error_message(self,text:str) -> None:
        """ Show an error message to the user, in status bar (vim-style)."""
        self.status_bar.set_long_message(text,error=True)

    def enter_command_mode(self,text:str) -> None:
        self.event_handler = CommandEntryEventHandler(self,text)
        self.status_bar.set_long_message(text)

    def exit_command_mode(self) -> None:
        self.event_handler = MainGameEventHandler(self)
        self.status_bar.set_long_message("")

    def get_cursor_input(self,final_action:CursorAction) -> None:
        self.cursor_entity.move_to(*self.player.pos)
        self.show_cursor = True
        self.event_handler = CursorMovementEventHandler(self,final_action)

    def finish_cursor_input(self) -> None:
        self.event_handler = MainGameEventHandler(self)
        self.show_cursor = False

    def handle_enemy_turns(self) -> None:
        # Reset status message and show log every turn. 
        self.status_bar.reset()
        self.message_log.display()

        self.turn += 1
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                for i in range(entity.moves_per_turn):
                    try:
                        entity.ai.perform()
                    except exceptions.Impossible:
                        pass

    def update_fov(self) -> None:
        """ Recompute visible area based on player's POV."""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x,self.player.y),
            radius=self.player.fov_radius,
            algorithm=tcod.FOV_BASIC,
        )
        self.game_map.explored |= self.game_map.visible

        # Also update other stuff here 'cause I'm not sure where else to do it.
        self.include_invisible_characters = self.player.fulfills("echolocate")
            

    def render(self, console:Console, context:Context):
        self.game_map.render(console)
        # A bit of a hack to enable t/f and possibly w/e movement
        # TODO Update this if I add any offset to the game map
        self.char_array = console.ch[0:self.game_map.width,0:self.game_map.height].copy()

        top_box_space = self.top_box_space

        # Render UI stuff
        render_stat_box(console,
            level_name=self.game_map.name,
            health=self.player.fighter.hp,
            max_health=self.player.fighter.max_hp,
            strength=self.player.fighter.strength,
            max_range=self.player.max_range,
            gold=self.player.gold,
            abilities=self.player.ability_string,
            AC=self.player.fighter.AC,
        )
        self.status_bar.render(console)
        self.text_window.render(console)
        if self.show_cursor:
            # Check whether cursor is within fov first
            #  TODO Handle explored-but-not-visible areas
            in_fov = self.game_map.visible[self.cursor]
            render_cursor(console,self.cursor,in_fov)

        context.present(console)
        console.clear()
