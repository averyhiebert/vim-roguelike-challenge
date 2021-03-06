""" A component for things to be triggered by various entity actions.

Mainly intended for auto-pickup gold, and landmines.
"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from components.base_component import BaseComponent
from components.inventory import Inventory
import exceptions
import colors

if TYPE_CHECKING:
    from entity import Actor, Item

class Trigger(BaseComponent):
    """ Item with various triggers, all empty by default."""
    parent: Item

    def entered(self,entity:Actor) -> None:
        """ Called when an actor enters the tile."""
        return None

    def exited(self,entity:Actor) -> None:
        """ Called when an actor exits the tile."""
        return None

    def yanked(self,entity:Actor) -> None:
        """ Called when yanked by `entity`."""
        return None

    def dropped(self,entity:Actor) -> None:
        """ Called when dropped by `entity`."""
        return None

class LambdaTrigger(Trigger):
    """ For making simple triggers quickly."""
    def __init__(self,*,
            entered:Optional[Function[[Item,Actor],None]]=None,
            exited:Optional[Function[[Item,Actor],None]]=None,
            yanked:Optional[Function[[Item,Actor],None]]=None,
            dropped:Optional[Function[[Item,Actor],None]]=None):
        super().__init__()
        if entered:
            self.entered = entered
        if exited:
            self.exited = exited
        if yanked:
            self.yanked = yanked
        if dropped:
            self.dropped = dropped

class GoldTrigger(Trigger):
    """ TODO Make enemies drop gold when they die."""
    def __init__(self,value:int):
        super().__init__()
        self.value = value

    def entered(self,entity:Actor) -> None:
        entity.gold += self.value
        if entity == entity.engine.player:
            entity.engine.message_log.add_message(
                f"You found {self.value} gold.")
        # Remove from map
        self.parent.gamemap.entities.remove(self.parent)

    def yanked(self,entity:Actor) -> None:
        entity.gold += self.value
        inventory = self.parent.parent # Should be an inventory, anyways
        inventory.remove(self.parent)

class LandmineTrigger(Trigger):
    """ Trigger unique to the landmine object."""
    def __init__(self):
        super().__init__()
        self.activated = False
        self.radius = 2
        self.damage = 12

    def entered(self,entity:Actor) -> None:
        if entity == entity.engine.player:
            self.activated = True
            text = "You hear the click of a landmine!"
            entity.engine.message_log.add_message(text,colors.very_bad)
            # Make trap visible
            self.parent.char = "^"
            entity.engine.show_error_message(text)

    def exited(self,entity:Actor) -> None:
        if self.activated and entity == entity.engine.player:
            self.parent.gamemap.entities.remove(self.parent)
            self.explode(entity)

    def yanked(self,entity:Actor) -> None:
        """ Note: safe to yank, as long as it's not activated."""
        if self.activated:
            inventory = self.parent.parent
            inventory.remove(self.parent)
            self.explode(entity)

    def dropped(self,entity:Actor) -> None:
        # TODO I suppose in the future it might be possible to
        #  drop something at a distance, but for now we assume
        #  that it was dropped on the same tile as the actor,
        #  in which case it will be immediately triggered.
        self.entered(entity)

    def explode(self,entity:Actor) -> None:
        entity.engine.message_log.add_message(
            f"The landmine detonated!",colors.bad
        )
        entity.gamemap.explosion(self.parent.pos,self.radius,self.damage)

class AltarTrigger(Trigger):
    def entered(self,entity:Actor) -> None:
        if entity == entity.engine.player and entity.fulfills("can win"):
            entity.engine.win_game()

class MessageTrigger(Trigger):
    def __init__(self,message:str):
        super().__init__()
        self.message = message

    def entered(self,entity:Actor) -> None:
        if entity == entity.engine.player:
            #entity.engine.show_message(self.message)
            entity.engine.show_tutorial_message(self.message)
