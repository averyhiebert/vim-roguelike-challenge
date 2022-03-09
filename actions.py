from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

from utils import roll_dice
import exceptions
import colors

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

class SaveGame(Action):
    def perform(self) -> None:
        self.skip_turn = True # No turn on save
        self.engine.save_as(fname="save.sav")
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
        #self.engine.text_window.show(summary,message_log_mode=True)
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
        

# Player actions =======================================================
class WaitAction(Action):
    def perform(self) -> None:
        pass

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

    def perform(self) -> None:
        """ TODO Figure out best way to still check for out-of-bounds in
        ignore_blocking mode."""
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

        self.entity.move_to(*destination)
        if len(self.path.points) > 2:
            self.entity.gamemap.add_trace(self.path.points)

class ActionDeleteAlongPath(ActionWithPath):
    def perform(self) -> None:
        self.path.truncate_to_navigable(self.entity)
        destination = self.path.last_occupiable_square(self.entity)

        # Move (TODO: Maybe this should be optional)
        self.entity.move_to(*destination)

        # Attack everything along path.
        for point in self.path.points:
            target = self.entity.gamemap.get_actor_at_location(point)
            if target and not (target == self.entity):
                target_x,target_y = point
                direction = (target_x - self.entity.x, target_y - self.entity.y)
                MeleeAction(self.entity,direction).perform()
        
        # Draw trace
        if len(self.path.points) > 2:
            self.entity.gamemap.add_trace(self.path.points,
                color=colors.delete_trace)

class PickupAlongPath(ActionWithPath):

    def __init__(self, entity:Entity, path:Path, register:Optional[str]=None):
        super().__init__(entity,path)
        self.register = register

    def perform(self) -> None:
        inventory = self.entity.inventory
        inserted = 0
        first = True
        # TODO There is probably a more efficient way to do this.
        # Must convert to list to iterate over,
        #  or else error "set changed size during iteration"
        for item in list(self.entity.gamemap.items):
            if item.pos in self.path.points:
                if first:
                    inventory.insert(item,self.register)
                    first=False
                else:
                    inventory.insert(item)
                inserted += 1
        if inserted == 0:
            raise exceptions.Impossible("There is nothing to yank.")
        # TODO: Should have a single combined message for all actions.

        # Draw trace
        if len(self.path.points) > 1:
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
    def perform(self) -> None:
        target = self.target_actor

        if not target:
            return # Nothing to attack

        to_hit = roll_dice(self.entity.fighter.to_hit)
        if to_hit > target.fighter.AC:
            damage = roll_dice(self.entity.fighter.damage)
            self.engine.message_log.add_message(
                f"{self.entity.name} attacked {target.name} ({damage} hp)."
            )
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(
                f"{self.entity.name} missed {target.name}."
            )

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
        self.engine.message_log.add_message(text)

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
