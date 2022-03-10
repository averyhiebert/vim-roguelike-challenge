""" For tracking a series of character inputs (representing a vim command)
and identifiying the appropriate resulting action."""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING
import re
import traceback

import numpy as np
import tcod

import actions
from exceptions import VimError, UserError
from path import Path

if TYPE_CHECKING:
    from engine import Engine

# TODO Maybe compile this
MOVEMENT_RE = r"(?P<zero>0)|(?P<repeat>[0-9]*)(?P<base>[hjkl]|;|[tf].|[we]|[HML$]|[`'].)"

def movement_reqs(command:str):
    """ Return a list of requirements for the given valid movement command.
    """
    m = re.match(MOVEMENT_RE,command)

    # Special case of 0
    if m.group("zero"):
        return ["0"]

    if m.group("base")[0] in "`'tf":
        # Don't include register or target char
        reqs = [m.group("base")[0]]
    else:
        reqs = [char for char in m.group("base")]
    return reqs

class VimCommandParser:

    def __init__(self,engine:Engine,movement_only=False,
            entity:Optional[Entity]=None):
        """ Use movement_only mode for situations that only require a movement,
        and not an action.

        entity should be player by default, but could be something else,
         e.g. cursor (the latter is only allowed in movement only mode
        """
        self.engine = engine
        self.movement_only = movement_only
        if not entity or not movement_only:
            entity = engine.player
        elif not movement_only and entity is not self.engine.player:
            raise RuntimeError("Invalid use of 'entity' param in vim parser")
        self.entity = entity

        # History needed for implementing "u"
        # Note: first position is a lie, ignore it.
        self.past_player_locations = []
        self.reset(update_history=False)

        self.last_tf_command = "" # For implementing ;

    def on_non_movement(self):
        """ Called every time we parse a partial command that is valid only as
        part of a non-movement action."""
        if self.movement_only:
            raise UserError(" Not a valid movement. ")


    def reset(self,update_history:bool=True):
        """ Only resets us back to be able to receive new commands, and
        updates the past location information.

        Does not reset the last_tf_command or other similar state that may
        be stored in the future."""
        if update_history:
            if len(self.past_player_locations) == 0:
                # No history,
                self.past_player_locations.append(self.entity.pos)
            if self.entity.pos != self.past_player_locations[-1]:
                # Update history
                self.past_player_locations.append(self.entity.pos)
        self.partial_command = "" # i.e. command so far

    def colon_command(self,command:str) -> Optional[Action]:
        """
        Parse a colon command and return an appropriate action.
        """
        self.reset()
        if command in [":reg",":registers"]:
            # Show inventory
            return actions.ShowInventory(self.entity)
        elif command in [":w",";write"]:
            # Save game
            return actions.SaveGame(self.entity)
        elif command in [":new",":new game"]:
            # Trigger a new game
            return actions.NewGame(self.entity)
        elif command in [":q",":quit"]:
            return actions.QuitGame(self.entity)
        elif command in [":q!",":quit!"]:
            return actions.HardQuitGame(self.entity)
        elif command in [":wq",":x"]:
            actions.SaveGame(self.entity).perform()
            return actions.QuitGame(self.entity)
        elif re.match(":swap (.) (.)", command):
            m = re.match(":swap (.) (.)", command)
            return actions.SwapRegisters(self.entity,m.group(1),m.group(2))
        elif command == ":godmode":
            # activate player god mode
            self.entity.enable_all()
            return actions.WaitAction(self.entity)
        elif command == ":set hlsearch":
            # TODO: This, and others, should be part of a general
            #  "GameCommandAction" with appropriate requirements.
            self.entity.engine.hlsearch = True
            return actions.WaitAction(self.entity)
        else:
            self.engine.exit_command_mode()
            raise VimError(command[1:])

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
            if char == " ":
                # Do nothing, but DO perform an enemy turn
                self.reset()
                return actions.WaitAction(self.entity)
        
        self.partial_command += char

        try:
            action = self.parse_partial_command() 
        except UserError as err:
            # No point printing the stack here
            self.reset()
            raise err
        except NotImplementedError as err:
            # Only temporary. Once all vim commands are implemented,
            #  this should be done away with.
            self.reset()
            raise err
        except Exception as err:
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

        player = self.entity
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
                target = (x,y + n)
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
                target = (x,y - n)
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
        #elif base[0] in "we":
            # TODO Implement this
            #raise NotImplementedError("w and e not implemented yet, sorry")
            #raise VimError("w and e are not yet implemented, sorry")
        #elif base[0] in "tf":
        if base[0] in "tfwe":
            if not n:
                n = 1

            mode = base[0] # t, f, w, or e
            if mode in "tf":
                target_char = base[-1]
                exclude_adjacent = (mode=="t")
            else:
                target_char = None # for w and e functionality
                exclude_adjacent = (mode=="w")

            possible_targets = engine.game_map.get_nearest(player.pos,
                target_char,exclude_adjacent=exclude_adjacent)

            # Closest n targets (to original starting location)
            targets = [player.pos] + possible_targets[:n]
        
            if len(targets) == 1:
                # This is not an "error," exactly, it just goes nowhere.
                targets.append(targets[0])
            else:
                # Handle the details of whether to overshoot/undershoot the
                #  final target, based on "t" or "f" mode.
                #   "w" and "e" have same behaviour as "t" and "f" respectively
                if mode in "we":
                    mode = "t" if mode=="w" else "f"
                targets[-1] = self.bump_destination(targets[-2],
                    targets[-1],mode)

            # Save in case of ;
            self.last_tf_command = command
            path = engine.game_map.get_poly_path(targets)
            return path
        elif base == ";":
            # Easy, just repeat saved command
            if self.last_tf_command:
                return self.parse_movement(self.last_tf_command)
            else:
                # A non-moving movement
                path = engine.game_map.get_mono_path(player.pos,player.pos)
                return path
        elif base[0] in "`'":
            # Move to mark
            target = engine.game_map.get_mark(base[1])
            if not target:
                # A non-moving movement
                target = player.pos
            path = engine.game_map.get_mono_path(player.pos,target)
            return path
        else:
            # TODO implement
            raise VimError(command)

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
        player = self.entity

        if source == target:
            return target
        if mode == "f" and engine.game_map.is_navigable(target,player):
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
        if engine.game_map.is_navigable(final_hope,player):
            return final_hope
        else:
            return target

    def parse_partial_command(self) -> Optional[Action]:
        """ 
        Parse the given partial vim command.
        
        For completed commands, return an appropriate Action.
        For incomplete (but potentially valid) commands, currently returns
         a Wait action, rather than none, because I still want the turn to
         advance.  But there may be some cases where I choose to change this.

        Otherwise, raise "invalid command" exception.

        When in movement_only mode, raise a user error on anything that is
         not a valid movement command.

        TODO: Need to solve the fact that every time I add a new command,
         I forget self.reset() and have trouble debugging it.

        To anyone (including me) who has to debug these regexes in the future:
          I am so sorry, please forgive me.
        """
        engine = self.engine
        command = self.partial_command
        player = self.entity

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
            self.reset()
            path = self.parse_movement(command)
            action = actions.ActionMoveAlongPath(player,path)
            action.requirements = movement_reqs(command)
            return action
        elif re.match(valid_pyd_re, command):
            self.on_non_movement()
            # A yank, pull, or delete
            self.reset()
            match = re.match(valid_pyd_re,command)
            main_command = match.group("command")

            # May or may not be a register
            register = None
            if match.group("register"):
                register = match.group("register")[1]

            if main_command == "dd":
                # A little area of effect attack for tight situations.
                #  (Currently, register does nothing.)
                #  (Maybe the register should, if specified, also yank
                #   the corpse when something dies? TODO that, maybe)
                offsets = [(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)]
                start = player.pos
                sx,sy = start
                aoe_path = Path(
                    [(sx+x,sy+y) for x,y in offsets] + [start],
                    game_map = engine.game_map
                )
                action = actions.ActionDeleteAlongPath(player,aoe_path)
                action.requirements = ["d","dd"]
                return action
            elif main_command[0] == "d":
                movement = match.group("movement")
                path = self.parse_movement(movement)

                action = actions.ActionDeleteAlongPath(player,path)
                action.requirements = movement_reqs(movement) + ["d"]
                return action
            elif main_command == "yy":
                path = Path([player.pos],game_map = engine.game_map)
                action = actions.PickupAlongPath(player,path,register)
                # No yy requirement, as that could be game-breaking
                return action
            elif main_command[0] == "y":
                movement = match.group("movement")
                path = self.parse_movement(movement)
                action = actions.PickupAlongPath(player,path,register)
                action.requirements = movement_reqs(movement) + ["y"]
                return action
            elif main_command == "p":
                item = player.inventory.get_item(register)
                return actions.DropItem(player,item)
            else:
                print(main_command)
                raise NotImplementedError("This command not implemented")
        elif re.match("m.",command):
            self.on_non_movement()
            # Set a mark in register .
            register = command[-1]
            self.reset()
            action = actions.ActionMakeMark(player,register)
            action.requirements = ["m"]
            return action
        elif command == "u":
            self.on_non_movement()
            # "Undo" (Move back to location prior to last move)
            if len(self.past_player_locations) == 0:
                # If no previous locations, do nothing/skip turn
                self.reset()
                return actions.WaitAction(player)
            target = self.past_player_locations.pop()
            self.reset(update_history=False)
            path = self.engine.game_map.get_mono_path(player.pos,
                target)
            action = actions.ActionMoveAlongPath(player,path)
            action.requirements = ["u"]
            return action
        elif re.match("@.",command):
            self.on_non_movement()
            self.reset()
            # Use an item.
            # Note: inventory may raise a vim error if register invalid.
            register = command[1]
            item = player.inventory.get_item(register)
            return actions.ItemAction(player,item)
        elif command in ":?/":
            self.on_non_movement()
            # Enter command mode
            self.reset()
            return actions.EnterCommandMode(player,command)
        elif command in ["gj","gk","G"]:
            self.on_non_movement()
            self.reset()
            return actions.TextScrollAction(player,command[-1:])
        elif command == "i":
            self.on_non_movement()
            # We treat this as shortcut for viewing inventory
            self.reset()
            return self.colon_command(":reg")
        elif command == "o":
            self.on_non_movement()
            self.reset()
            return actions.ObserveAction(player)
        elif command == "ZZ":
            # Save and quit
            self.reset()
            actions.SaveGame(self.entity).perform()
            return actions.QuitGame(self.entity)

        # Checks for valid partial commands (which don't do anything):
        #   TODO Check for cases that we don't want to penalize with an
        #   enemy turn; maybe selecting registers, for instance?
        #   In those cases, do not return an action.
        elif re.match(partial_valid_movement_re,command):
            return actions.WaitAction(player)
        elif re.match(partial_valid_pyd_re,command):
            self.on_non_movement()
            return actions.WaitAction(player)
        elif command in "m@Z":
            # Some straggler/singleton possibilities
            self.on_non_movement()
            return actions.WaitAction(player)
        elif command == "g":
            # Special case, since we don't want enemy action when
            #  scrolling through the message log.
            return None
        else:
            raise VimError(command)

