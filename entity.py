from typing import Tuple

class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    def __init__(self, x:int, y:int, char:str, 
            color:Tuple[int,int,int]=(255,255,255)):
        self.x = x
        self.y = y
        self.char = char
        self.color = color

    def move_to(self,dest_x,dest_y) -> None:
        self.x = dest_x
        self.y = dest_y
