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

    def reset(self):
        self.short_message = ""
        self.long_message = ""
        self.error = False

    def set_short_message(self,text:str,error=False):
        self.short_message = text
        self.long_message = ""
        self.error=error

    def set_long_message(self,text:str,error=False):
        self.long_message = text
        self.error=error

    def render(self,console:Console):
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
            x,y = self.engine.player.pos
            position_text = f"{x:2d},{y:2d}"
            console.print(x=38,y=38,string=position_text,fg=fg,bg=bg)
            position = "Top"
            console.print(50-len(position) - 1,y=38,string="Top",fg=fg,bg=bg)
            console.print(x=1,y=38,string=self.short_message,fg=fg,bg=bg)


