from components.base_component import BaseComponent

class Fighter(BaseComponent):
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
