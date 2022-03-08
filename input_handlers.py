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
    CommandModeStringChanged,
    NextPageAction,
    ActionMoveAlongPath,
    MoveCursorAction,
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
    TODO Dvorak and other layouts, maybe?
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
        #self.do_enemy_turn = False

    def ev_keydown(self, event: tcod.event.KeyDown) -> Tuple[Optional[Action],bool]:
        action: Optional[Action] = None
        player = self.engine.player

        key = event.sym
        usable_key = keydown_to_char(event) # i.e. an ascii char

        if usable_key:
            action = self.command_parser.next_key(usable_key)
        elif key == tcod.event.K_ESCAPE:
            action = EscapeAction(player)

        return action

class CommandEntryEventHandler(EventHandler):
    """ Used when entering a / or : command."""

    def __init__(self, engine:Engine,text:str):
        super().__init__(engine)
        self.text=text
        self.command_parser = VimCommandParser(engine=engine)

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
            if self.text[0] == ":":
                action = self.command_parser.colon_command(self.text)
                ExitCommandMode(player).perform() # Also necessary
            elif self.text[0] == "/":
                ExitCommandMode(player).perform() # Also necessary
                raise NotImplementedError()
            self.text = ""
        elif key == tcod.event.K_ESCAPE:
            action = EscapeAction(player)
        return action

class CursorMovementEventHandler(EventHandler):
    """ Event handler for moving a cursor (e.g. for "observe" or
    possibly for some targeting effects).

    Allows movement commands but not other commands.

    At the end of its life, calls callback before returning to normal operation.
    """
    def __init__(self, engine:Engine,final_action:CursorAction):
        super().__init__(engine)
        self.command_parser = VimCommandParser(engine=engine,
            movement_only=True)
        self.final_action = final_action

    def ev_keydown(self, event: tcod.event.KeyDown) -> Tuple[Optional[Action],bool]:
        action: Optional[Action] = None
        player = self.engine.player

        key = event.sym
        usable_key = keydown_to_char(event) # i.e. an ascii char

        if usable_key == "o" or key == tcod.event.K_RETURN:
            # Exit cursor mode
            self.engine.finish_cursor_input()
            return self.final_action
        elif usable_key:
            #action = self.command_parser.next_key(usable_key)
            action = self.command_parser.next_key(usable_key)
            if isinstance(action,ActionMoveAlongPath):
                return MoveCursorAction(action)
            else:
                return None
        elif key == tcod.event.K_ESCAPE:
            action = EscapeAction(player)

        return action


class TextWindowPagingEventHandler(EventHandler):
    def ev_keydown(self,event:tcod.event.KeyDown) -> Optional[Action]:
        is_char = bool(keydown_to_char(event))
        if is_char or event.sym == tcod.event.K_RETURN:
            # On a character input or enter key, advance to next page.
            action = NextPageAction(self.engine.player)
            pass
        elif event.sym == tcod.event.K_ESCAPE:
            action = EscapeAction(self.engine.player)
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
