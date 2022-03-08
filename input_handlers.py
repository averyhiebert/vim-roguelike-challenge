from __future__ import annotations

import traceback

from typing import Optional
from typing import Optional, TYPE_CHECKING

import tcod.event

from actions import (
    Action,
    BumpAction,
    EscapeAction,
    EnterCommandMode,
    ExitCommandMode,
    CommandModeStringChanged
)
from vim_parser import VimCommandParser
from exceptions import VimError

if TYPE_CHECKING:
    from engine import Engine

def keydown_to_char(event:tcod.event.KeyDown) -> Optional[str]:
    """Convert keydown event to a character (including correct
    handling of shift key).

    Also converts arrow keys to vim directions (hjkl).
    
    Returns None for non alphanumeric/punctuation characters
    (e.g. backspace etc.)
    
    TODO Is it worth also supporting capslock?  Probably not.
    """
    symbols = "`1234567890-=[]\;',./"
    shift_symbols = '~!@#$%^&*()_+{}|:"<>?'
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    unshifted_letters = "abcdefghijklmnopqrstuvwxyz"
    arrow_to_letter = {
        "Up":"k","Down":"j","Left":"h","Right":"l"
    }

    shift_pressed = (event.mod & tcod.event.Modifier.SHIFT)
    label = event.sym.label

    if label == "Space":
        return " "
    elif label in arrow_to_letter:
        return arrow_to_letter[label]
    elif label in symbols:
        if shift_pressed:
            return shift_symbols[symbols.index(label)]
        else:
            return label
    elif label in letters:
        if shift_pressed:
            return label
        else:
            return unshifted_letters[letters.index(label)]
            
    return None


class EventHandler(tcod.event.EventDispatch[Action]):

    def __init__(self, engine:Engine):
        self.engine = engine

    def handle_events(self) -> None:
        for event in tcod.event.wait(timeout=0.1):
            # Note: timeout allows us to do some mild animation
            action = self.dispatch(event)
            do_enemy_turn = True

            if not action:
                # Don't do anything if there's nothing to do!
                return

            if action:
                # Note: exceptions here will still be caught by Main and
                #  shown to player.  Enemy turn will not be performed if there
                #  is an exception during the player's turn.
                action.perform()
                do_enemy_turn = not action.skip_turn

            if do_enemy_turn:
                # We only do this for certain actions.
                #  (e.g. checking inventory does not trigger enemy turn)
                # (This logic may be unnecessary, though? Need to think
                #  about it a bit more.)
                self.engine.handle_enemy_turns()
                do_enemy_turn = False

            self.engine.update_fov() # Update FOV before player's next turn

    def ev_quit(self,event:tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

class MainGameEventHandler(EventHandler):
    def __init__(self, engine:Engine):
        super().__init__(engine)
        self.command_parser = VimCommandParser(engine=engine)
        self.do_enemy_turn = False

    def ev_keydown(self, event: tcod.event.KeyDown) -> Tuple[Optional[Action],bool]:
        action: Optional[Action] = None
        player = self.engine.player

        key = event.sym
        usable_key = keydown_to_char(event) # i.e. an ascii char

        if usable_key:
            try:
                action = self.command_parser.next_key(usable_key)
            except VimError as err:
                # TODO Should print message to user, either in the
                #  message log or in the bottom left where vim does.
                print(err)
        elif key == tcod.event.K_ESCAPE:
            action = EscapeAction(player)

        return action

class CommandEntryEventHandler(EventHandler):
    """ Used when entering a / or : command."""

    def __init__(self, engine:Engine,text:str):
        super().__init__(engine)
        self.text=text

    def ev_keydown(self, 
            event: tcod.event.KeyDown) -> Tuple[Optional[Action],bool]:
        action: Optional[Action] = None
        player = self.engine.player

        key = event.sym
        usable_key = keydown_to_char(event) # i.e. an ascii char

        if usable_key:
            self.text += usable_key
            action = CommandModeStringChanged(player,self.text)
        elif key == tcod.event.K_BACKSPACE:
            self.text = self.text[:-1]
            if self.text == "":
                action = ExitCommandMode(player)
            else:
                action = CommandModeStringChanged(player,self.text)
        elif key == tcod.event.K_RETURN:
            # TODO Try executing command.
            self.text = ""
            action = ExitCommandMode(player)
        elif key == tcod.event.K_ESCAPE:
            action = EscapeAction(player)
        return action


class GameOverEventHandler(EventHandler):
    def handle_events(self) -> None:
        for event in tcod.event.wait():
            action = self.dispatch(event)
            
            if action is None:
                continue

            action.perform()

    def ev_keydown(self, event:tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None
        key = event.sym

        if key == tcod.event.K_ESCAPE:
            action = EscapeAction(self.engine.player)

        return action
