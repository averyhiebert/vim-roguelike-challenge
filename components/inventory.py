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
        self.register_history = []

    @property
    def items(self) -> List[item]:
        """ Returns a COPY of the list of items in the inventory.

        This is a change from the tutorial, to follow the vim register
        system.  I am trying to make the player inventory resemble vim
        registers, but still make everything compatible with the tutorial
        when it comes to enemy inventories.
        """
        return list(self.registers.values())

    def get_last_used_register(self) -> Optional[str]:
        """ Return the register last used that still contains stuff.

        In the process, clears out anything empty in the register history.
        """
        if len(self.register_history) == 0:
            return None
        candidate = self.register_history[-1]
        if candidate in self.registers:
            return candidate
        else:
            self.register_history.pop()
            return self.get_last_used_register()

    def get_item(self,register:Optional[str]=None):
        if not register:
            reg = self.get_last_used_register()
            if reg:
                return self.get_item(reg)
            else:
                # Must be the start of the game. Return item 1
                return self.get_item("1")
        if register in self.registers:
            return self.registers[register]
        elif register not in self.valid_registers:
            raise exceptions.VimError()
        raise exceptions.Impossible(f"Nothing in \"{register}!")

    def remove(self,item:Item) -> str:
        """ Remove an item from inventory without necessarily dropping
        it (e.g. after eating a consumable).

        Returns the register of the item that was dropped.
        """
        for key,value in list(self.registers.items()):
            if value is item:
                del self.registers[key]
                return key
        else:
            raise RuntimeError("Tried to remove item not in inventory")

    def drop(self,item:Item) -> None:
        """ Remove item from inventory and drop it on ground.
        """
        register = self.remove(item) # Note: may throw exception, which is intended
        item.place(self.parent.pos, self.gamemap)
        self.engine.message_log.add_message(
            f"You dropped the {item.name} (\"{register})")

    def insert(self, item:Item,register:Optional[str]=None,
            silent=False) -> None:
        """ Add an item to the inventory.
        """
        if len(self.items) >= self.capacity:
            raise exceptions.Impossible("Your inventory is full.")

        # Remove item from old parent
        item.parent.gamemap.entities.remove(item)
        item.parent = self

        if register and register in self.registers:
            raise exceptions.Impossible(f"\"{register} is full.")
        elif register and register in self.valid_registers:
            self.registers[register] = item
        elif register:
            raise exceptions.VimError()
        else:
            # Add to first open register (in order)
            for key in self.valid_registers:
                if key not in self.registers:
                    register = key
                    self.registers[key] = item
                    break
        self.register_history.append(register)
        if not silent:
            self.parent.gamemap.engine.message_log.add_message(f"You yanked the {item.name} (\"{register})")
