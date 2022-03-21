""" The status bar at the bottom of the window.

Handles its own rendering as well (seemed more straightforward).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from tcod.console import Console

import colors
#from render_functions import render_bottom_text

class StatusBar:
    def __init__(self,engine:Engine):
        self.engine = engine
        self.long_message = ""  #(e.g. an error or / and : commands)
        self.short_message = "" #(e.g. "register q", -- INSERT --, etc.
        self.error = False # Whether we're showing an error message.
        self.tutorial=False # Whether we're showing a tutorial message.
        self.skip_next_reset = False # To ensure error messages stick around

    def reset(self) -> None:
        if self.skip_next_reset:
            self.skip_next_reset = False
            return
        self.short_message = ""
        self.long_message = ""
        self.error = False

    def set_short_message(self,text:str,error=False) -> None:
        self.short_message = text
        self.long_message = ""
        self.error=error

    def set_long_message(self,text:str,error=False,tutorial=False) -> None:
        self.long_message = text
        self.error=error
        self.tutorial=tutorial
        if error or tutorial:
            self.skip_next_reset=True

    def render(self,console:Console) -> None:
        """ Render to screen."""
        #
        fg = colors.ui_fg
        bg = colors.default_bg

        if self.long_message != "":
            if self.error:
                fg = colors.error_fg
                bg = colors.error_bg
            text = self.long_message
            console.print(x=1,y=38,string=text,fg=fg,bg=bg)
        else:
            # Render default text, i.e. the x,y and %/top/etc.
            #  TODO Figure out what the %/top/bottom/all represents.
            #  Maybe progress towards the final level?
            x,y = self.engine.coords_to_show
            position_text = f"{x:2d},{y:2d}"
            console.print(x=33,y=38,string=position_text,fg=fg,bg=bg)
            progress = self.engine.game_world.progress_summary
            console.print(x=42,y=38,string=f"{progress:>6}",fg=fg,bg=bg)
            console.print(x=1,y=38,string=self.short_message,fg=fg,bg=bg)


