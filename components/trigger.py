""" A component for things to be triggered by various entity actions.

Mainly intended for auto-pickup gold, and landmines.
"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from components.base_component import BaseComponent
from components.inventory import Inventory
import exceptions

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
            entered:Optional[Function[[Item,Actor],None]],
            exited:Optional[Function[[Item,Actor],None]],
            yanked:Optional[Function[[Item,Actor],None]],
            dropped:Optional[Function[[Item,Actor],None]]):
        super().__init__(entity)
        self.entered = entered
        self.exited = exited(x)
        self.yanked = yanked(x)
        self.dropped = dropped(x)

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
