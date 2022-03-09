from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import actions
from components.base_component import BaseComponent
from components.inventory import Inventory
from components.ability import Ability

import exceptions
import utils

if TYPE_CHECKING:
    from entity import Actor, Item

class Consumable(BaseComponent):
    parent: Item

    def get_action(self, consumer: Actor) -> Optional[actions.Action]:
        """Try to return the action for this item."""
        return actions.ItemAction(consumer, self.parent)

    def activate(self, action:actions.ItemAction) -> None:
        """Invoke this item's ability.
        """
        raise NotImplementedError()

    def consume(self) -> None:
        item = self.parent
        inventory = item.parent
        if isinstance(inventory,Inventory):
            inventory.remove(item)

class NotConsumable(Consumable):
    """ A consumable that does nothing but print a message.

    Crucially, it does not remove itself from parent inventory."""
    def __init__(self,message:str):
        self.message = message

    def consume(self) -> None:
        raise exceptions.Impossible(self.message)

    def activate(self,action:actions.ItemAction) -> None:
        raise exceptions.Impossible(self.message)

class HealingConsumable(Consumable):
    def __init__(self, amount:int):
        self.amount = amount

    def activate(self, action:actions.ItemAction) -> None:
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                f"You consumed the {self.parent.name}, recovering {amount_recovered} hp"
            )
            self.consume()
        else:
            raise Impossible(f"Your health is already full.")
