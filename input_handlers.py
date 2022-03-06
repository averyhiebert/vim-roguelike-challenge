from __future__ import annotations

from typing import Optional
from typing import Optional, TYPE_CHECKING

import tcod.event

from actions import Action, BumpAction, EscapeAction
from vim_parser import VimCommandParser

if TYPE_CHECKING:
    from engine import Engine

class EventHandler(tcod.event.EventDispatch[Action]):

    def __init__(self, engine:Engine):
        self.engine = engine
        self.command_parser = VimCommandParser(engine=engine)
    
    @staticmethod
    def keydown_to_char(event:tcod.event.KeyDown) -> Optional[str]:
        """Convert keydown event to a character (including correct
        handling of shift key).

        Also converts arrow keys to vim directions (hjkl).
        
        Returns None for non alphanumeric/punctuation characters
        (e.g. backspace etc.)
        
        TODO Is it worth also supporting capslock?  Probably not.
        """
        symbols = "`1234567890-=[]\;',./ "
        shift_symbols = '~!@#$%^&*()_+{}|:"<>? '
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        unshifted_letters = "abcdefghijklmnopqrstuvwxyz"
        arrow_to_letter = {
            "Up":"k","Down":"j","Left":"h","Right":"l"
        }

        shift_pressed = (event.mod & tcod.event.Modifier.SHIFT)
        label = event.sym.label

        if label in arrow_to_letter:
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

    def handle_events(self) -> None:
        for event in tcod.event.wait():
            action = self.dispatch(event)

            if action is None:
                continue

            action.perform()

            self.engine.handle_enemy_turns()
            self.engine.update_fov() # Update FOV before player's next turn

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        player = self.engine.player

        usable_key = self.keydown_to_char(event)

        if usable_key == "i":
            # TODO
            print("TODO Open the inventory")
        elif usable_key == "o":
            print("TODO Observe/look around")
        elif usable_key:
            action, do_turn = self.command_parser.next_key(usable_key)

        elif key == tcod.event.K_ESCAPE:
            action = EscapeAction(player)

        return action
