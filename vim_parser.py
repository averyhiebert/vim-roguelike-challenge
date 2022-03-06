""" For tracking a series of character inputs (representing a vim command)
and identifiying the appropriate resulting action."""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING
import re

from actions import BumpAction, DummyAction, ActionMoveAlongPath

if TYPE_CHECKING:
    from engine import Engine

def parse_movement(match,engine:Engine) -> Path:
    """ Given the re match for a valid movement,
    return a Path corresponding to the given movement.
    """
    directions = {
        "j":(0,1),
        "k":(0,-1),
        "h":(-1,0),
        "l":(1,0),
    }

    player = engine.player
    if match.group("zero"):
        # Command is just 0
        # Move all the way to the left.
        far_left = (0,player.y)
        path = engine.game_map.get_mono_path(player.pos,far_left)
        path.truncate_to_navigable(player)
        return path
    
    n:Optional[int] = None # Note: n will never be 0, so "if n:" is fine
    if match.group("repeat"):
        n = int(match.group("repeat"))

    base = match.group("base")

    if base in directions:
        if not n:
            n = 1
        dx,dy = directions[base]
        player = engine.player
        target = (player.x + n*dx, player.y + n*dy)
        path = engine.game_map.get_mono_path(player.pos,target)
        path.truncate_to_navigable(player)
        return path
    elif base == "H":
        # TODO More "dry" for 0HML$
        top = (player.x,0)
        base_path = engine.game_map.get_mono_path(player.pos,top)
        base_path.truncate_to_navigable(player)
        if n:
            #TRY to go down by given value
            end = base_path.end
            x,y = end
            target = (x,y + (n - 1))
            sub_path = engine.game_map.get_mono_path(end,target)
            sub_path.truncate_to_navigable(player)
            final_dest = sub_path.end
            return engine.game_map.get_mono_path(player.pos,final_dest)
        else:
            return base_path
    elif base == "L":
        bottom = (player.x,engine.game_map.height)
        base_path = engine.game_map.get_mono_path(player.pos,bottom)
        base_path.truncate_to_navigable(player)
        if n:
            #TRY to go down by given value
            end = base_path.end
            x,y = end
            target = (x,y - (n - 1))
            sub_path = engine.game_map.get_mono_path(end,target)
            sub_path.truncate_to_navigable(player)
            final_dest = sub_path.end
            return engine.game_map.get_mono_path(player.pos,final_dest)
        else:
            return base_path
    elif base == "$":
        start = player.pos
        if n:
            # Go down by n-1 lines and *then* go right.
            #  Note: must start from left and pick first valid spot from right
            #  (Chance of no valid option on that line; in this rare case, 
            #    raise an error even though technically there is still a way
            #    to interpret this validly. TODO Do it properly.)
            start = (player.x, player.y + (n-1))

        right = (engine.game_map.width,start[1])
        path = engine.game_map.get_mono_path(start,right)
        path.truncate_to_navigable(player)
        return path
    else:
        # TODO implement
        raise NotImplementedError("This movement not implemented")

def parse_partial_command(command:str,engine:Engine) -> Optional[Action]:
    """ 
    Parse the given partial vim command.
    
    For completed commands, return an appropriate Action.
    For incomplete (but potentially valid) commands, return None.

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

    if re.match(valid_movement_re,command):
        """
        if command in directions:
            # Simplest case
            return BumpAction(engine.player,directions[command])
        else:"""
        match = re.match(valid_movement_re,command)
        path = parse_movement(match,engine)
        return ActionMoveAlongPath(engine.player,path)
    elif re.match(valid_pyd_re,command):
        raise NotImplementedError("This command not implemented")
        #return DummyAction(engine.player)
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
                # Do nothing, but DO perform an enemy turn
                return DummyAction(self.engine.player)
        
        self.partial_command += char

        try:
            action = parse_partial_command(self.partial_command,self.engine) 
            if action:
                self.reset()
        except Exception as err:
            # TODO check for correct exception
            self.reset()
            raise err

        return action
