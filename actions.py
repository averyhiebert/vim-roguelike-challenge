from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

from utils import roll_dice
import exceptions
import colors
from entity import Gold

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity

class Action:
    def __init__(self, entity:Actor,skip_turn:bool=False,
            requirements:List[str]=[]) -> None:
        super().__init__()
        self.entity = entity
        self.requirements = requirements
        self.skip_turn = skip_turn # True if action does not expend a turn

    @property
    def engine(self) -> Engine:
        """ Return the engine this action belongs to."""
        return self.entity.gamemap.engine

    def perform(self) -> None:
        """ Perform this action with the objects needed to determine
        its scope.

        `self.engine` is the scope the action is being performed in.
        `self.entity` is the one performing the action.

        Must be overridden by subclasses.
        """
        raise NotImplementedError()

    def first_failure(self) -> Optional[str]:
        """Check whether the given entity fulfills the requirements
        for this action.

        Return the first failed requirement, or None if all pass
        """
        for r in self.requirements:
            if not self.entity.fulfills(r):
                return r
        else:
            return None


# UI/Modal actions ===================================================

class EscapeAction(Action):
    def perform(self) -> None:
        # TODO Make sure this makes sense in other modes (e.g. cursor, :)
        #QuitGame(self.entity).perform()
        raise exceptions.UserError("Type :quit<Enter> to exit vim")

class StartGame(Action):
    def __init__(self,entity:Actor,starter_class:str):
        super().__init__(entity,skip_turn=True)
        self.starter_class = starter_class

    def perform(self) -> None:
        self.engine.start_game(self.starter_class)

class SaveGame(Action):
    def perform(self) -> None:
        self.skip_turn = True # No turn on save
        self.engine.save_as(fname="vimrc.sav")
        self.engine.status_bar.set_short_message(
            f" Game written to <save.sav>")

class HardQuitGame(Action):
    def perform(self) -> None:
        raise SystemExit()

class QuitGame(Action):
    def perform(self) -> None:
        self.skip_turn = True
        if self.engine.last_save < self.engine.turn:
            raise exceptions.UserError(
                "E37: No write since last change (add ! to override)")
        raise SystemExit()

class NewGame(Action):
    def perform(self) -> None:
        # TODO Should erase old save file.
        self.skip_turn = True # Pointless, I guess
        raise exceptions.NewGame("Bad hack to communicate with main()")

class EnterCommandMode(Action):
    """ Action to start entering a / or : command."""
    def __init__(self,entity:Actor,text:str):
        super().__init__(entity,skip_turn=True)
        self.text = text

    def perform(self) -> None:
        self.engine.enter_command_mode(self.text)

class ExitCommandMode(Action):
    """ Action to stop entering a / or : command."""
    def __init__(self,entity:Actor):
        super().__init__(entity,skip_turn=True)

    def perform(self) -> None:
        self.engine.exit_command_mode()

class CommandModeStringChanged(Action):
    """ Used when typing a letter in command mode."""
    def __init__(self,entity:Actor,text:str):
        super().__init__(entity,skip_turn=True)
        self.text = text

    def perform(self) -> None:
        self.engine.status_bar.set_long_message(self.text)

class ShowInventory(Action):
    def __init__(self,entity:Actor):
        super().__init__(entity,skip_turn=True)

    def perform(self) -> None:
        summary = self.entity.inventory.get_summary()
        self.engine.text_window.show(summary,message_log_mode=False)

class NextPageAction(Action):
    """ Move to next page when viewing multi-page text."""
    def __init__(self,entity:Actor):
        super().__init__(entity,skip_turn=True)

    def perform(self) -> None:
        self.engine.text_window.next_page()

class TextScrollAction(Action):
    """ For scrolling the message log or other scroll-able text."""
    def __init__(self,entity:Actor,text:str):
        super().__init__(entity,skip_turn=True)
        self.text=text

    def perform(self) -> None:
        self.engine.text_window.scroll(self.text)

# "Spells"/colon command actions:
class KillAll(Action):
    def __init__(self,entity:Actor,visible_only=True,drop_corpse=False):
        super().__init__(entity,skip_turn=False)
        self.visible_only = visible_only
        self.drop_corpse=drop_corpse
        self.requirements = [":s"]

    def perform(self):
        gm = self.entity.gamemap
        targets = [a for a in gm.actors 
            if a != self.entity and (gm.entity_visible(a) or not self.visible_only)]
        for t in targets:
            t.corpse_drop_chance = float(self.drop_corpse)
            t.fighter.die()

class SellDroppedItems(Action):
    def perform(self) -> None:
        """ Convert all visible dropped amulets and spells to gold."""
        # TODO Varying values
        gm = self.entity.gamemap
        for item in list(gm.items):
            if item.char in '"?' and gm.entity_visible(item):
                # TODO Remove self and spawn gold
                gold = Gold(5)
                gold.spawn(gm,*item.pos)
                gm.entities.remove(item)

class SetHLSearchAction(Action):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.requirements = [":set hlsearch"]

    def perform(self) -> None:
        self.entity.engine.hlsearch=True
        self.entity.engine.message_log.add_message(
            "hlsearch is now on.",fg=colors.important)

class Upgrade(Action):
    def __init__(self,*args,to_upgrade:str,**kwargs):
        super().__init__(*args,**kwargs)
        self.to_upgrade = to_upgrade.lower()
        self.skip_turn = False

    def perform(self) -> None:
        if self.to_upgrade not in ["strength","ac","armour","armor","range"]:
            if self.to_upgrade in ["hp","health"]:
                # Just in case someone tries
                raise exceptions.UserError(f"Cannot upgrade {self.to_upgrade}")
            elif self.to_upgrade == "gold":
                raise exceptions.UserError(f"It was worth a shot.")
            else:
                raise exceptions.UserError(f"Unknown property {self.to_upgrade}")
        if self.entity.gold >= 10:
            if self.to_upgrade == "strength":
                self.entity.fighter.strength += 1
            elif self.to_upgrade in ["ac","armour","armor"]:
                self.entity.fighter.AC += 2
            elif self.to_upgrade == "range":
                self.entity.max_range += 1
            else:
                raise RuntimeError("Something went wrong.")
            self.entity.gold -= 10
        else:
            raise exceptions.Impossible(f"Upgrading costs 10 gold")

# Player actions =======================================================
class WaitAction(Action):
    def perform(self) -> None:
        pass

class TakeStairsAction(Action):
    def __init__(self,*args,up=False,**kwargs):
        super().__init__(*args,**kwargs)
        self.up = up

    def perform(self) -> None:
        """ Take the stairs, if any exist here."""
        if self.up:
            if self.entity.pos == self.engine.game_map.upstairs_location:
                self.engine.game_world.prev_floor()
                self.engine.message_log.add_message(
                    "You ascend the staircase.",
                )
            else:
                raise exceptions.Impossible("There are no stairs here.")
        elif self.entity.pos == self.engine.game_map.downstairs_location:
            self.engine.game_world.next_floor()
            self.engine.message_log.add_message(
                "You descend the staircase."
            )
        else:
            raise exceptions.Impossible("There are no stairs here.")

class DummyAction(Action):
    """ An action that does nothing, but can potentially signal that
    no enemy turn is to be performed in response to the latest event.
    
    Currently the same as WaitAction, I guess."""

    def perform(self) -> None:
        pass

class ActionMakeMark(Action):
    """ Make a mark (as in commands m and `)  on the current gamemap."""
    def __init__(self,entity:Entity,register:str):
        super().__init__(entity)
        self.register = register

    def perform(self) -> None:
        self.entity.gamemap.make_mark(self.register,self.entity.pos)
        

class ActionWithPath(Action):
    """ An action that acts along a path of player movement."""
    def __init__(self, entity:Entity, path:Path):
        super().__init__(entity)
        self.path = path

    def perform(self) -> None:
        raise NotImplementedError()

class ActionMoveAlongPath(ActionWithPath):
    """ Move to end of path."""
    def __init__(self,entity:Entity,path:Path,ignore_blocking=False):
        """
        ignore_blocking mode is mainly intended for cursor movement, but there
        may be other uses as well.
        """
        super().__init__(entity=entity,path=path)
        self.ignore_blocking = ignore_blocking
        self.register=None

    def perform(self) -> None:
        if self.ignore_blocking:
            self.path.truncate_to_navigable(self.entity)
            destination = self.path.end
        else:
            self.path.truncate_to_navigable(self.entity)
            destination = self.path.last_occupiable_square(self.entity)
        
        if len(self.path.points) >= 2 and destination == self.path.points[-2]:
            # Possibly a melee attack
            target_x,target_y = self.path.points[-1]
            direction = (target_x - self.entity.x, target_y - self.entity.y)
            # Would be nicer if MeleeAction took a destination, not direction,
            #  but oh well...
            if not self.ignore_blocking:
                MeleeAction(self.entity,direction).perform()

        # Yank, if magnetic
        #  (Comes before move, so you don't automatically die to landmines)
        if self.entity.fulfills("magnetic"):
            PickupAlongPath(self.entity,self.path,
                register=self.register,
                draw_trace=False).perform()
        
        # Actually move
        self.entity.move_to(*destination)
        if len(self.path.points) > 2:
            self.entity.gamemap.add_trace(self.path.points)


class ActionDeleteAlongPath(ActionWithPath):
    def __init__(self,*args,no_truncate:bool=False,
            register:Optional[str]=None,**kwargs):
        super().__init__(*args,**kwargs)
        self.no_truncate = no_truncate
        self.register=register

    def perform(self) -> None:
        if not self.no_truncate:
            self.path.truncate_to_navigable(self.entity)
        destination = self.path.last_occupiable_square(self.entity)

        # Attack everything along path.
        for point in self.path.points:
            target = self.entity.gamemap.get_actor_at_location(point)
            if target and not (target == self.entity):
                target_x,target_y = point
                direction = (target_x - self.entity.x, target_y - self.entity.y)
                MeleeAction(self.entity,direction).perform()

        # Yank, if magnetic
        # (We do this before moving, so as to yank landmines before landing on
        #  them, but after the attack so that we're yanking corpses and not
        #  the enemies themselves.  Yanking enemies is not implemented yet,
        #  but I have plans to possibly maybe add it in the future.)
        if self.entity.fulfills("magnetic"):
            PickupAlongPath(self.entity,self.path,
                register=self.register,
                draw_trace=False).perform()

        # Move, unless a ranged weapon is equipped
        if not self.entity.fulfills("ranged"):
            self.entity.move_to(*destination)

        # Draw trace
        if len(self.path.points) > 1:
            self.entity.gamemap.add_trace(self.path.points,
                color=colors.delete_trace)

class PickupAlongPath(ActionWithPath):

    def __init__(self, entity:Entity, path:Path,
            register:Optional[str]=None,
            draw_trace=True):
        super().__init__(entity,path)
        self.register = register
        self.draw_trace=draw_trace

    def perform(self) -> None:
        inventory = self.entity.inventory
        inserted = 0
        first = True
        # TODO There is probably a more efficient way to do this.
        # Note: Must convert iterator to list,
        #  or else "set changed size during iteration" error
        for item in list(self.entity.gamemap.items):
            if item.pos in self.path.points:
                if first:
                    inventory.insert(item,self.register)
                    first=False
                else:
                    inventory.insert(item)
                inserted += 1
        if inserted == 0:
            #raise exceptions.Impossible("There is nothing to yank.")
            # Actually, is there any real reason to consider this an error?
            pass

        # Draw trace
        if len(self.path.points) > 1 and self.draw_trace:
            self.entity.gamemap.add_trace(self.path.points,
                color=colors.yank_trace)

class ActionWithDirection(Action):
    def __init__(self, entity:Actor, direction: Tuple[int,int]):
        # Note: action with direction never skips a turn
        super().__init__(entity)
        self.direction = direction

    def perform(self) -> None:
        raise NotImplementedError()

    @property
    def dx(self):
        return self.direction[0]
        
    @property
    def dy(self):
        return self.direction[1]

    @property
    def dest(self):
        """ Returns this action's destination."""
        return (self.entity.x + self.dx, self.entity.y + self.dy)

    @property
    def blocking_entity(self) -> Optional[Entity]:
        """ Return the blocking entity at this action's destination."""
        return self.engine.game_map.get_blocking_entity_at_location(self.dest)

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this action's destination."""
        return self.engine.game_map.get_actor_at_location(self.dest)

class MovementAction(ActionWithDirection):
    def perform(self) -> None:

        if not self.engine.game_map.in_bounds(self.dest):
            return # Destination out of bounds
        if not self.engine.game_map.tiles["walkable"][self.dest]:
            return # Destination blocked by a tile
        if self.blocking_entity:
            return # Destination blocked by entity
        self.entity.move_to(*self.dest)

class MeleeAction(ActionWithDirection):
    # TODO Add optional steal=True flag to allow stealing.
    def perform(self) -> None:
        target = self.target_actor

        if not target:
            return # Nothing to attack

        damage = self.entity.fighter.strength

        # Deal full damage for anything above target AC
        full_damage = max(0,damage-target.fighter.AC)
        remaining = damage - full_damage
        # Deal half damage for anything above half of target AC
        #  (No damage from attacks below a quarter of AC)
        half_damage = (max(0,remaining - (target.fighter.AC//2)))//2
        total_damage = full_damage + half_damage
        flavourtext = self.entity.fighter.attack_text
        if target == self.engine.player:
            fg = colors.bad
        else:
            fg=colors.normal
        self.engine.message_log.add_message(
            f"{self.entity.name} {flavourtext} {target.name} ({total_damage} hp).",fg
        )
        target.fighter.hp -= total_damage

# TODO: Figure out whether this is still needed?
#  Although, enemies still use it even if player doesn't.
class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.target_actor:
            return MeleeAction(self.entity,self.direction).perform()
        else:
            return MovementAction(self.entity,self.direction).perform()

class RegexSearch(Action):
    def __init__(self,entity:Entity,regex:str):
        super().__init__(entity,skip_turn=True)
        self.regex = regex

    def perform(self) -> None:
        # TODO: Let the player keep track of the points as well.
        points = self.engine.game_map.regex_search(self.regex)
        self.engine.game_map.set_highlight(points)

class SwapRegisters(Action):
    def __init__(self,entity:Entity,reg_a:str,reg_b:str):
        super().__init__(entity,skip_turn=False)
        self.reg_a = reg_a
        self.reg_b = reg_b

    def perform(self) -> None:
        self.entity.inventory.swap(self.reg_a,self.reg_b)


# Cursor Actions (weird) ========================================

class MoveCursorAction(ActionWithPath):
    """ Moves the cursor to a given location."""
    def __init__(self,original:ActionMoveAlongPath):
        """ Given a player movement action, copy its path but move
        the cursor rather than the player.
        """
        super().__init__(original.entity,original.path)
        self.skip_turn=True
        self.original = original
        self.original.ignore_blocking = True

    def perform(self) -> None:
        self.original.entity = self.engine.cursor_entity
        self.original.perform()

class GetCursorInput(Action):
    def __init__(self, entity:Entity,final_action:CursorAction):
        super().__init__(entity)
        self.final_action = final_action
        self.skip_turn = True

    def perform(self) -> None:
        self.entity.engine.get_cursor_input(final_action=self.final_action)

class CursorAction(Action):
    """ An action that requires a cursor position.

    Will be performed twice (first to switch into cursor mode,
    then to do something with the cursor).

    Must implement perform2 as the second "performance"
    
    No difference implementation-wise from a regular Action,
    just doing this for type-checking reasons.
    """
    def __init__(self,entity:Entity):
        super().__init__(entity)
        self.second_use = False
        self.skip_turn = True

    def perform(self) -> None:
        if not self.second_use:
            self.second_use = True
            GetCursorInput(self.entity,self).perform()
        else:
            self.perform2()

    def perform2(self) -> None:
        raise NotImplementedError()


class ObserveAction(CursorAction):
    def perform2(self) -> None:
        target = self.engine.cursor
        text = self.engine.game_map.describe_tile(target,visible_only=True)
        text = f"You see: {text}"
        self.engine.message_log.add_message(text,colors.important)

# Item Actions =========================================================

class ItemAction(Action):
    def __init__(
            self, entity:Actor, item:Item,
            target_pos:Optional[Tuple[int,int]]=None) -> None:
        super().__init__(entity)
        self.item = item
        if not target_pos:
            target_pos = entity.pos
        self.target_pos = target_pos

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at the target destination."""
        return self.engine.game_map.get_actor_at_location(self.target_pos)

    def perform(self) -> None:
        self.item.consumable.activate(self)

class DropItem(ItemAction):
    def perform(self) -> None:
        self.entity.inventory.drop(self.item)
