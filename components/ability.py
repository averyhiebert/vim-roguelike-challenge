"""
Basic architectural idea:

Actors (basically just the player) can have "intrinsic" Abilities.
Additionally, Items can have abilities.

An actor has access to the abilities of any items that they have equipped
in their inventory, in addition to any "intrinsic" abilities that they have. 

In general, when the player executes a command some TBD function will check
for the requisite abilities.  A requirement string will be passed to the
Ability, and it will return True/False regarding whether it satisfies the
requirement string.  Requirement string could be something simple like "d",
or more complex, like a regex search.

In retrospect, these are really more like status effects.  If I were to
do this again, these would be "effects" with various subclasses,
and players/inventories would have "fulfills(effect)" method. But for 7drl
this system is good enough.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import BaseComponent

class Ability(BaseComponent):
    def fulfills(self,requirement:str) -> bool:
        """ Return true if this Ability is sufficient to meet the
        given requirement.
        """
        raise NotImplementedError()

    def name(self) -> str:
        """ Return a (short) string summary of the ability, which can be
        displayed to the user in a list of currently-active abilities.
        """
        raise NotImplementedError()

class Omnipotent(Ability):
    def fulfills(self,requirement:str) -> bool:
        return True
    def name(self) -> str:
        return "All abilities"

class AllCommands(Ability):
    def fulfills(self,requirement:str) -> bool:
        """ Return true for any short command (i.e. 1 or 2 characters).

        TODO Improve this if I add short status effects that aren't commands
        """
        return len(requirement) <= 2
    def name(self) -> str:
        return "all commands"

class SimpleAbility(Ability):
    def __init__(self,requirement_string:str):
        """ Fulfills only the requirement specified by requirement_string.
        
        E.G. if requirement_string = "H", that presumably means that this
          Ability allows the player to use the "H" command.
        """
        super().__init__()
        self.requirement_string = requirement_string

    def fulfills(self,requirement:str) -> Bool:
        return requirement == self.requirement_string

    def name(self) -> str:
        return self.requirement_string
        
