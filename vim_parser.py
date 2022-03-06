""" For tracking a series of character inputs (representing a vim command)
and identifiying the appropriate resulting action."""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING
import re
import traceback

import numpy as np
import tcod

from actions import BumpAction, WaitAction, ActionMoveAlongPath, ActionMakeMark

if TYPE_CHECKING:
    from engine import Engine

# TODO Maybe compile this
MOVEMENT_RE = r"(?P<zero>0)|(?P<repeat>[0-9]*)(?P<base>[hjkl]|;|[tf].|[we]|[HML$]|[`'].)"

class VimError(Exception):
    pass

class VimCommandParser:

    def __init__(self,engine:Engine):
        self.engine = engine
        self.reset()

        self.last_tf_command = "" # For implementing ;

    def invalid(self,message="Invalid command."):
        self.reset()
        raise NotImplementedError(message)

    def reset(self):
        self.partial_command = "" # i.e. command so far

    def next_key(self,char:str) -> Optional[Action]:
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
                self.reset()
                return WaitAction(self.engine.player)
        
        self.partial_command += char

        try:
            action = self.parse_partial_command() 
        except VimError as err:
            self.reset()
            raise err
        except Exception as err:
            # TODO check for correct exception
            traceback.print_exc()
            self.reset()
            raise err

        return action

    def parse_movement(self,command:str) -> Path:
        """ Given the re match for a valid movement,
        return a Path corresponding to the given movement.

        Note: I assume path truncation is the job of the movement Action.

        In cases where the player goes nowhere, returns a length 1 path.
        """
        engine = self.engine
        match = re.match(MOVEMENT_RE,command)
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
            return path
        elif base == "H":
            # TODO More "dry" for 0HML$
            top = (player.x,0)
            base_path = engine.game_map.get_mono_path(player.pos,top)
            base_path.truncate_to_navigable(player)
            if n:
                #TRY to go down by given value
                x,y = base_path.end
                target = (x,y + (n - 1))
                return engine.game_map.get_mono_path(player.pos,target)
            else:
                return base_path
        elif base == "L":
            bottom = (player.x,engine.game_map.height)
            base_path = engine.game_map.get_mono_path(player.pos,bottom)
            base_path.truncate_to_navigable(player)
            if n:
                #Try to move up by given value
                x,y = base_path.end
                target = (x,y - (n - 1))
                return engine.game_map.get_mono_path(player.pos,target)
            else:
                return base_path
        elif base == "$":
            start = player.pos
            if n:
                # Implementing this properly will be annoying and it doesn't
                #  seem like a very important feature, so I just won't bother.
                # 
                # TODO Proper behavour: Go down by n-1 lines and *then* go right.
                pass
            right = (engine.game_map.width,start[1])
            path = engine.game_map.get_mono_path(start,right)
            return path
        elif base == "M":
            # Note: numbers do nothing here
            # Also, I have made the executive decision to go to the center of
            #  the map, not just centered vertically.
            path = engine.game_map.get_mono_path(player.pos,engine.game_map.center)
            return path
        elif base[0] in "tf":
            if not n:
                n = 1

            mode = base[0] # should be t or f
            target_char = base[-1]
            exclude_adjacent = (mode=="t")

            possible_targets = engine.game_map.get_nearest(player.pos,
                target_char,exclude_adjacent=exclude_adjacent)

            # Closest n targets (to original starting location)
            targets = [player.pos] + possible_targets[:n]
        
            if len(targets) == 1:
                # This is not an "error," exactly, it just goes nowhere.
                target_location = targets[0]
            else:
                # Handle the details of whether to overshoot/undershoot the
                #  final target, based on "t" or "f" mode.
                targets[-1] = self.bump_destination(targets[-2],
                    targets[-1],mode)

            # Save in case of ;
            self.last_tf_command = command
            path = engine.game_map.get_poly_path(targets)
            return path
        elif base == ";":
            # Easy, just repeat saved command
            return self.parse_movement(self.last_tf_command)
        elif base[0] in "`'":
            # Move to mark
            target = engine.game_map.get_mark(base[1])
            if not target:
                # A non-moving movement
                target = player.pos
            path = engine.game_map.get_mono_path(player.pos,target)
            return path

        elif base[0] in "we":
            # TODO Implement this
            #raise NotImplementedError()
            raise VimError("w and e are not yet implemented, sorry")
        else:
            # TODO implement
            raise VimError("Unknown command")

    def bump_destination(self,source:Tuple[int,int],
            target:Tuple[int,int],mode:str) -> Tuple[int,int]:
        """ Decide whether to "overshoot", "undershoot", or land exactly
        on target, based on mode "t" or "f".

        With "t", we always undershoot (unless source == target)

        With "f", we overshoot IF it's blocked, unless the overshoot
         location is also blocked, in which case we just land directly on target
         and let the subsequent move action figure out what to do with that.
        """
        engine = self.engine
        if source == target:
            return target
        if mode == "f" and engine.game_map.is_navigable(target,engine.player):
            return target
        
        tx, ty = target
        candidates = [(tx + x,ty + y) for x in [-1,0,1] for y in [-1,0,1]
                        if (x,y) != (0,0)]
        # sort closest-to-furthest
        candidates.sort(key=lambda c:np.linalg.norm(np.array(source)-c))

        if mode=="t":
            # Return closest
            return candidates[0]

        # Note: remaining cases are all f
        for c in candidates:
            # Can return any target that includes target in the path.
            if target in [(x,y) for x,y in tcod.los.bresenham(source,c)]:
                final_hope = c
                break
        else:
            final_hope = candidates[-1]
        if engine.game_map.is_navigable(final_hope,engine.player):
            return final_hope
        else:
            return target
        

    def parse_partial_command(self) -> Optional[Action]:
        """ 
        Parse the given partial vim command.
        
        For completed commands, return an appropriate Action.
        For incomplete (but potentially valid) commands, return None.

        Otherwise, raise "invalid command" exception.

        To anyone (including me) who has to debug these regexes in the future:
          I am so sorry, please forgive me.
        """
        engine = self.engine
        command = self.partial_command

        directions = {
            "j":(0,1),
            "k":(0,-1),
            "h":(-1,0),
            "l":(1,0),
        }

        # Matches something that can be parsed to give a movement
        valid_movement_re = MOVEMENT_RE

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
        partial_valid_movement_re = r"([0-9]|$)*(([hjkl]|$)|([tf;]|$)(.|$)|([we]|$)|([HML$]|$)|([`']|$)(.|$))"
        partial_valid_pyd_re = r'(("|$)(.|$))?((p|$)|(y|$)(y|$)|(d|$)(d|$)|([yd]|$)(' + partial_valid_movement_re + '))'

        if re.match(valid_movement_re,command):
            # Basic movement
            match = re.match(valid_movement_re, command)
            path = self.parse_movement(command)
            self.reset()
            return ActionMoveAlongPath(engine.player,path)
        elif re.match(valid_pyd_re, command):
            # A yank, pull, or delete
            self.reset()
            raise NotImplementedError("This command not implemented")
        elif re.match("m.",command):
            # Set a mark in register .
            register = command[-1]
            self.reset()
            return ActionMakeMark(engine.player,register)

        # Checks for valid partial commands (which don't do anything):
        #   TODO Check for cases that we don't want to penalize with an
        #   enemy turn; maybe selecting registers, for instance?
        #   In those cases, do not return an action.
        elif re.match(partial_valid_movement_re,command):
            return WaitAction(engine.player)
        elif re.match(partial_valid_pyd_re,command):
            return WaitAction(engine.player)
        elif command in "m":
            # Some straggler/singleton possibilities
            return WaitAction(engine.player)
        else:
            raise VimError("Invalid command.")

