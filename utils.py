"""Just some helpful utils that I'm not sure belong to any particular class."""
from typing import Iterator, Tuple

import random
import math
from itertools import product

def roll_dice(dice:str) -> int:
    """ Rolls strings of the form 1d4+3d6+72 """
    dice = dice.split("+")
    total = 0
    for die in dice:
        parts = die.split("d")
        if len(parts) == 1:
            total += int(die)
        elif len(parts) == 2:
            total += sum([random.randint(1,int(parts[1])) 
                for i in range(int(parts[0])) ])
    return total

def a_or_an(s:str) -> str:
    """ Return 'a [str]' or 'an [str]' as appropriate."""
    return f"an {s}" if s[0] in "aeiouAEIOU" else f"a {s}"

def aoe_by_radius(center:Tuple[int,int],radius:int) -> Iterator[Tuple[int,int]]:
    """ Iterator of points starting at `center`, tracing out a square
    area of the given radius, and returning to center."""
    x,y = center

    yield center
    yield from ((x+i,y+j)  for i,j in product(range(-radius,radius+1),repeat=2))
    yield center

def distance(p1,p2):
    x1,y1 = p1
    x2,y2 = p2
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)
