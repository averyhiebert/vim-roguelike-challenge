"""Just some helpful utils that I'm not sure belong to any particular class."""
import random

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
        
