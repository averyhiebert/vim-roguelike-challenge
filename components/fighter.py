from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import BaseComponent
from render_order import RenderOrder
from input_handlers import GameOverEventHandler

if TYPE_CHECKING:
    from entity import Actor



class Fighter(BaseComponent):
    entity: Actor

    def __init__(self,hp:int,AC:int,to_hit:str,damage:str):
        self.max_hp = hp
        self._hp = hp
        self.AC = AC
        self.to_hit = to_hit
        self.damage = damage

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value:int) -> None:
        self._hp = max(0,min(value,self.max_hp))
        if self._hp == 0 and self.entity.ai:
            self.die()

    def die(self) -> None:
        if self.engine.player is self.entity:
            death_message = "You died!"
            self.engine.event_handler = GameOverEventHandler(self.engine)
        else:
            death_message = f"{self.entity.name} is dead!"

        # TODO Replace with a yankable, consumable corpse object
        self.entity.char = "%"
        self.entity.color = (191,0,0)
        self.entity.blocks_movement = False
        self.entity.name = f"{self.entity.name} corpse"
        self.entity.ai = None
        self.entity.summary = f"The consumable remains of the {self.entity.name}"
        self.entity.render_order = RenderOrder.CORPSE
        self.engine.message_log.add_message(death_message)
