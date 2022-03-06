""" For leaving a fading bg-coloured area on the map,
mainly to help visualize actions, but possibly also for explosions etc."""

from typing import List, Tuple
import time
import numpy as np

import colors


class MapTrace:
    def __init__(self,points:List[Tuple[int,int]],
            color:Tuple[int,int,int]=colors.default_trace,
            fade_time:float=1.0):
        """ A coloured area on the map that should fade after a set amount
        of time."""
        self.points = points
        self.start_color = np.array(color)
        # TODO: Should expire based on game turn, not time.
        self.fade_time = fade_time # Measured in seconds
        self.creation_time = time.time() 

    @property
    def expired(self):
        return self.elapsed_time > self.fade_time

    @property
    def elapsed_time(self):
        return time.time() - self.creation_time


    def get_color(self,bg:Tuple[int,int,int]) -> Tuple[int,int,int]:
        """Get the bg color for the trace by lerping between
        start colour and bg colour, based on fade time."""
        if self.expired:
            return bg
        else:
            dt = self.elapsed_time/self.fade_time
            bg = np.array(bg)
            r,g,b = self.start_color + dt*(bg - self.start_color)
            return (int(r),int(g),int(b))
