from __future__ import annotations

from typing import List, TYPE_CHECKING

from components.base_component import BaseComponent
import exceptions

if TYPE_CHECKING:
    from entity import Actor, Item

class Inventory(BaseComponent):
    parent: Actor

    def __init__(self, capacity:int):
        """ Note: capacity must be <= 35."""
        self.capacity = capacity
        self.valid_registers = "123456789abcdefghijklmnopqrstuvwxyz"[:capacity]
        self.registers:Dict[str,Item] = {}

    @property
    def items(self) -> List[item]:
        """ Returns a COPY of the list of items in the inventory.

        This is a change from the tutorial, to follow the vim register
        system.  I am trying to make the player inventory resemble vim
        registers, but still make everything compatible with the tutorial
        when it comes to enemy inventories.
        """
        return list(self.registers.values())

    def drop(self,item:Item) -> None:
        """ Remove item from inventory and drop it on ground.
        """
        for key,value in registers:
            if value is item:
                del self.registers[key]
        else:
            raise RuntimeError("Tried to delete item not in inventory.")
        item.place(self.parent.x, self.parent.y, self.gamemap)
        self.engine.message_log.add_message(f"You dropped the {item.name}.")

    def insert(self, item:Item) -> None:
        """ Add an item to the inventory.
        """
        if len(self.items) >= self.capacity:
            raise exceptions.Impossible("Your inventory is full.")

        # Remove item from old parent
        item.parent.gamemap.entities.remove(item)
        item.parent = self.parent.inventory

        # Add to first open register (in order)
        for key in self.valid_registers:
            if key not in self.registers:
                self.registers[key] = item
                break
        self.parent.gamemap.engine.message_log.add_message(f"You yanked the {item.name}")
