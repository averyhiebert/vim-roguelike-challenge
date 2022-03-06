""" For tracking a series of character inputs (representing a vim command)
and identifiying the appropriate resulting action."""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING
import re

from actions import BumpAction

if TYPE_CHECKING:
    from engine import Engine

def parse_partial_command(command:str,engine:Engine) -> Optional[Action]:
    """ 
    Parse the given partial vim command.
    
    If it is a complete command, return an appropriate Action.  
    If a valid (but incomplete) command, return None.
    Otherwise, raise "invalid command" exception.

    To anyone (including me) who has to debug these regexes in the future:
      I am so sorry, please forgive me.
    """
    directions = {
        "j":(0,1),
        "k":(0,-1),
        "h":(-1,0),
        "l":(1,0),
    }


    # Matches something that can be parsed to give a movement
    valid_movement_re = r"(?P<zero>0)|(?P<repeat>[0-9]*)(?P<base>[hjkl]|[tf].|[we]|[HML$]|[`'].)"

    # Matches a prefix for yank or delete (or put)
    #  (For now I'm not allowing "put" with movement, since that's not a thing
    #   in actual vim, but I may allow it for gameplay reasons later.)

    # Note also: I am allowing any character for the register, and checking
    #  whether it's a "valid" register will be done elsewhere, to allow for
    #  more helpful error messages and/or more flexibility later.
    #  Same goes for markers.

    # Note also: You *can* specify a register before deleting, but I don't know
    #  what exactly it'll do.  Maybe attack with whatever's in that register?
    valid_pyd_re = r'(?P<register>".)?(?P<command>p|yy|dd|[yd](?P<movement>' + valid_movement_re + '))'

    # To understand the partial regexes, see:
    #  https://stackoverflow.com/questions/42461651/partial-matching-a-string-against-a-regex
    # I'm sure it could be simplified, but I simply do not want to think about
    #  this any longer.
    partial_valid_movement_re = r"([0-9]|$)*(([hjkl]|$)|([tf]|$)(.|$)|([we]|$)|([HML$]|$)|([`']|$)(.|$))"
    partial_valid_pyd_re = r'(("|$)(.|$))?((p|$)|(y|$)(y|$)|(d|$)(d|$)|([yd]|$)(' + partial_valid_movement_re + '))'

    #print(f"DEBUG partial: {command}")

    if re.match(valid_movement_re,command):
        #print(f"Valid movement!")
        if command in directions:
            # Simplest case
            return BumpAction(engine.player,directions[command])
        else:
            # TEMP just to reset
            return BumpAction(engine.player,(0,1))
    elif re.match(valid_pyd_re,command):
        print(f"Valid command!")
        # TEMP just to reset
        return BumpAction(engine.player,(0,1))
    elif re.match(partial_valid_movement_re,command):
        # TODO Check for cases that we don't want to penalize with an
        #  enemy turn; maybe selecting registers, for instance?
        return None
    elif re.match(partial_valid_pyd_re,command):
        # Note: the different forms of partial command are separate cases
        #  solely to maintain SOME level of readability.
        return None
    else:
        raise ValueError("Invalid command.")

class VimCommandParser:

    def __init__(self,engine:Engine):
        self.engine = engine
        self.reset()

    def invalid(self,message="Invalid command."):
        self.reset()
        raise NotImplementedError(message)

    def reset(self):
        self.partial_command = "" # i.e. command so far

    def next_key(self,char:str) -> Tuple[Optional[Action],bool]:
        """ 
        Take a *single* character and continue parsing the vim command being
        entered.

        The optional action returned represents the action resulting from
        the command (only once the command has been fully entered).

        The boolean indicates whether or not a turn has been expended.

        TODO The question of whether an action takes a turn should be
          moved to the Action object. Then a dummy action taking no turn
          can be returned by the parser if necessary.
        """
        direction = {
            "j":(0,1),
            "k":(0,-1),
            "h":(-1,0),
            "l":(1,0),
        }

        if self.partial_command == "":
            # We are starting a brand-new command
            if char in "io:/":
                # TODO these all need to trigger special modes
                self.reset()
                raise NotImplementedError(f"{char} mode not yet implemented")
            elif char == " ":
                # No action, but DO perform an enemy turn
                return (None,True)
        
        self.partial_command += char

        try:
            action = parse_partial_command(self.partial_command,self.engine) 
            if action:
                self.reset()
        except Exception as err:
            # TODO check for correct exception
            self.reset()
            raise err

        return (action,True)
