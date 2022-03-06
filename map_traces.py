""" For leaving a fading bg-coloured area on the map,
mainly to help visualize actions, but possibly also for explosions etc."""

from typing import List, Tuple
import time
import numpy as np

import colors


class MapTrace:
    def __init__(self,points:List[Tuple[int,int]],
            start_color:Tuple[int,int,int]=colors.default_trace,
            fade_time:float=1.0):
        """ A coloured area on the map that should fade after a set amount
        of time."""
        self.points = points
        self.start_color = np.array(start_color)
        # TODO: Should expire based on game turn, not time.
        self.fade_time = fade_time # Measured in seconds
        self.creation_time = time.time() 

    @property
    def expired(self):
        return (time.time() - self.creation_time > self.fade_time)

    def get_color(self):
        """Get the bg color for the trace.

        (This could maybe involve lerping at some point, once I figure out
         how I want to handle animations, but for now it's just this.)"""
        return self.start_color
            
