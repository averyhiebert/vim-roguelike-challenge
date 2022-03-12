from __future__ import annotations

from typing import List, TYPE_CHECKING

from components.base_component import BaseComponent
from components.ability import Ability
import exceptions

if TYPE_CHECKING:
    from entity import Actor, Item

#class Inventory(BaseComponent,Ability):
class Inventory(Ability):
    parent: Actor

    def __init__(self, capacity:int):
        """ Note: capacity must be <= 35."""
        self.capacity = capacity
        self.valid_registers = "123456789abcdefghijklmnopqrstuvwxyz"[:capacity]
        self.equipped_registers = "123456789"
        self.registers:Dict[str,Item] = {}
        self.register_history = []

    def fulfills(self,requirement:str) -> Bool:
        for item in self.equipped:
            if item.fulfills(requirement):
                return True
        else:
            return False

    @property
    def items(self) -> List[item]:
        """ Returns a COPY of the list of items in the inventory.

        This is a change from the tutorial, to follow the vim register
        system.  I am trying to make the player inventory resemble vim
        registers, but still make everything compatible with the tutorial
        when it comes to enemy inventories.
        """
        return list(self.registers.values())

    @property
    def equipped(self) -> List[item]:
        """ Returns a list of items that are equipped (i.e. in
        registers 1 to 9).
        """
        return [v for k,v in self.registers.items() 
            if k in self.equipped_registers]

    def swap(self,a,b) -> None:
        """ Swap the two given registers. """
        if a in self.registers and b in self.registers:
            self.registers[b],self.registers[a] = self.registers[a], self.registers[b]
        elif a in self.registers:
            self.registers[b] = self.registers[a]
            del self.registers[a]
        elif b in self.registers:
            self.registers[a] = self.registers[b]
            del self.registers[b]
        elif a in self.valid_registers and b in self.valid_registers:
            # Swap nothing with nothing
            pass
        else:
            raise exceptions.Impossible("Invalid register.")
        self.parent.engine.message_log.add_message(
            f'Swapped "{a} and "{b}')

    def get_summary(self) -> List[str]:
        """ Return a list of lines summarizine the contents of
        the inventory in human-readable form.

        TODO Use colours?
        """
        lines = [
            f"{self.parent.name} inventory",
            len(f"{self.parent.name} inventory")*"~",
            " ",
            "Equipped:"
        ]
        for key in self.equipped_registers:
            if key in self.registers:
                lines.append(f" {key}) {self.registers[key].name}")
        lines.extend([" ","Unequipped:"])
        for key in "abcdefghijklmnopqrstuvwxyz":
            if key in self.registers:
                lines.append(f" {key}) {self.registers[key].name}")
        return lines

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
            raise exceptions.RegisterError(register)
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
        # Trigger drop behaviour, if any.
        item.trigger.dropped(self.parent)

    def insert(self, item:Item,register:Optional[str]=None,
            silent=False,startup=False) -> None:
        """ Add an item to the inventory.

        Startup should be true when we are inserting items at startup, rather
        than within a game, i.e. for starting classes.
        """
        if not item.yankable:
            # Do nothing
            # TODO Some sort of exception, or maybe I just shouldn't use
            #  the Item class for things that aren't meant to be yankable
            return
        if len(self.items) >= self.capacity:
            raise exceptions.Impossible("Your inventory is full.")

        if register and register in self.registers:
            raise exceptions.Impossible(f"\"{register} is full.")
        elif register and register in self.valid_registers:
            self.registers[register] = item
        elif register:
            raise exceptions.RegisterError(register)
        else:
            # Add to first open register (in order)
            for key in self.valid_registers:
                if key not in self.registers:
                    register = key
                    self.registers[key] = item
                    break
        # Remove item from old parent
        if not startup:
            item.parent.gamemap.entities.remove(item)
        item.parent = self

        self.register_history.append(register)
        if not (silent or startup):
            self.parent.gamemap.engine.message_log.add_message(f"You yanked the {item.name} (\"{register})")

        # Trigger yank behaviour, if any.
        if not startup:
            item.trigger.yanked(self.parent)
