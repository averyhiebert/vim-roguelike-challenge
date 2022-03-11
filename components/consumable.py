from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import actions
from components.base_component import BaseComponent
from components.inventory import Inventory
from components.ability import Ability
from vim_parser import VimCommandParser

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
    def __init__(self, amount:int,hp_buff:bool=False):
        self.amount = amount
        self.hp_buff = hp_buff # Whether to permanently increase hp

    def activate(self, action:actions.ItemAction) -> None:
        consumer = action.entity
        if self.hp_buff:
            consumer.fighter.max_hp += self.amount

        amount_recovered = consumer.fighter.heal(self.amount)

        if self.hp_buff:
            self.engine.message_log.add_message(
                f"You consumed the {self.parent.name}, increasing your max hp by {self.amount}"
            )
            self.consume()
        elif amount_recovered > 0:
            self.engine.message_log.add_message(
                f"You consumed the {self.parent.name}, recovering {amount_recovered} hp"
            )
            self.consume()
        else:
            raise exceptions.Impossible(f"Your health is already full.")

class CommandConsumable(Consumable):
    def __init__(self,command:str):
        super().__init__()
        self.command = command

    def activate(self, action:actions.ItemAction) -> None:
        """Invoke this item's ability.
        """
        consumer = action.entity
        parser = VimCommandParser(consumer.engine,entity=consumer)
        action = parser.colon_command(self.command)
        action.requirements = [] # Make sure player can do it
        # (Although I'm not sure whether requirements even get checked during
        #  perform(), vs at some other point?)
        action.perform()
        self.consume()
