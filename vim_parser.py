""" For tracking a series of character inputs (representing a vim command)
and identifiying the appropriate resulting action."""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from enum import auto, Enum

from actions import BumpAction

class VimCommandType(Enum):
    """ For keeping track of the type of command being constructed."""
    INIT = auto()
    MOVEMENT = auto()
    DELETE = auto()
    YANK = auto()
    PUT = auto()


class VimCommandParser:


    def __init__(self,engine:Engine):
        self.engine = engine

        self.command_type = VimCommandType.INIT
        self.number = "" # i.e. used for tracking 4l et cetera

    def fail(self,message="Invalid command."):
        raise NotImplementedError(message)

    def reset(self):
        self.command_type = VimCommandType.INIT
        self.number = ""

    def next_key(self,char:str) -> Tuple[Optional[Action],bool]:
        """ 
        Take a *single* character and continue parsing the vim command being
        entered.

        The optional action returned represents the action resulting from
        the command (only once the command has been fully entered).

        The boolean indicates whether or not a turn has been expended.
        """
        direction = {
            "j":(0,1),
            "k":(0,-1),
            "h":(-1,0),
            "l":(1,0),
        }

        if self.command_type == VimCommandType.INIT:
            # We are starting a brand-new command
            if char in direction:
                # Just basic movement
                self.reset()
                return (BumpAction(self.engine.player,direction[char]),True)
            elif char in "123456789":
                # Number + movement
                self.number += char
                self.command_type = VimCommandType.MOVEMENT
                return (None,True)
            else:
                # TODO d,y,p, and others
                self.fail()
        else:
            self.fail()
