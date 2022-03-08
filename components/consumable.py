from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import actions
from components.base_component import BaseComponent
from components.inventory import Inventory
from exceptions import Impossible

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
