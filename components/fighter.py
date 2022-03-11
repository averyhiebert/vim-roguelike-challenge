from __future__ import annotations

from typing import TYPE_CHECKING
import random

from components.base_component import BaseComponent
from render_order import RenderOrder
from input_handlers import GameOverEventHandler
from entity import Corpse

if TYPE_CHECKING:
    from entity import Actor



class Fighter(BaseComponent):
    parent: Actor

    def __init__(self,hp:int,AC:int,strength:int,
            hp_buff:bool=False,attack_text:str="hit"):
        self.max_hp = hp
        self._hp = hp
        self.AC = AC
        self.strength = strength
        self.hp_buff = hp_buff # Whether the corpse buffs hp
        self.attack_text=attack_text # e.g. hit, bit, stabbed, etc.

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value:int) -> None:
        self._hp = max(0,min(value,self.max_hp))
        if self._hp == 0 and self.parent.ai:
            # TBH, I am not clear on what the point of checking parent.ai is,
            #  but it's in the tutorial and I'm following it on the assumption
            #  that they did it that way on purpose.
            self.die()

    def die(self) -> None:
        if self.engine.player is self.parent:
            # Should save, to prevent save scumming/ensure permadeath.
            death_message = "You died! Press (q) to quit, or (n) to start a new game."
            self.engine.event_handler = GameOverEventHandler(self.engine)
            # Note: must log BEFORE saving
            self.engine.message_log.add_message(death_message)
            self.engine.save_as()
        else:
            death_message = f"{self.parent.name} is dead!"
            self.engine.message_log.add_message(death_message)

        # Possibly spawn a corpse
        if random.random() < self.parent.corpse_drop_chance:
            corpse = Corpse(self.parent)
            corpse.spawn(corpse.gamemap,*corpse.pos)
        # Remove self from map
        self.parent.gamemap.entities.remove(self.parent)

    def heal(self,amount:int) -> None:
        if self.hp == self.max_hp:
            return 0

        new_hp = min(self.max_hp,self.hp + amount)
        amount_recovered = new_hp - self.hp

        self.hp = new_hp
        return amount_recovered

    def take_damage(self, amount:int) -> None:
        self.hp -= amount
