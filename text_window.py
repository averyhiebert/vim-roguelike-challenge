""" The window for displaying text on the right.

Used by the message log, and sometimes other things.

Enters a "press any key to continue" state when displaying text
too long to fit in the window.

Handles its own rendering as well (seemed more straightforward).
"""
from __future__ import annotations

from typing import TYPE_CHECKING
import textwrap
import math

import colors
from input_handlers import MainGameEventHandler, TextWindowPagingEventHandler

if TYPE_CHECKING:
    from engine import Engine
    from tcod.console import Console

class TextWindow:
    def __init__(self,engine:Engine,x:int=0,y:int=0,width:int=10,height:int=10):
        self.engine = engine
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Stuff for pagination
        self.pages:List[List[Tuple[str,Tuple[int,int]]]] = []
        self.current_page = 0
        self.message_log_mode = False
        self.max_lines = 1000

    def next_page(self):
        self.current_page += 1
        if self.current_page >= len(self.pages) - 1:
            # Exit modal mode.
            self.engine.event_handler = MainGameEventHandler(self.engine)
            # Display the message log by default
            #self.engine.message_log.display()

    def show(self,texts:Union[List[str],List[Tuple[str,Tuple[int,int,int]]]],
            message_log_mode=False):
        """ Begin showing the text. Texts can be either strings, or
         tuples of (string, color).

        In message log mode, all messages go on one page 
         but TODO allow scrolling up and down.
        
        In normal mode, if necessary we enter an input-handling mode
        based on "press any key to continue" behaviour.

        If provided, length of `colors` must match length of `messages`.
        """
        self.message_log_mode = message_log_mode
        if len(texts) == 0:
            # Nothing to show.
            self.pages = []
            self.current_page = 0
            return

        color_included = isinstance(texts[0],tuple)

        # Set up the pagination

        self.current_page = 0
        page_height = self.height - 1
        final_lines = []
        for item in texts:
            if color_included:
                line, color = item
            else:
                line = item
                color = colors.ui_fg
            wrapped_lines = textwrap.wrap(
                line, self.width, expand_tabs=True, subsequent_indent=" "
            )
            final_lines.extend([(l,color) for l in wrapped_lines])

        if not self.message_log_mode:
            page_height = self.height - 1 # (To leave room for "-- More --")
        else:
            page_height = len(final_lines)
        total_pages = math.ceil(len(final_lines)/page_height)

        self.pages = [final_lines[i*page_height:i*page_height+page_height] for i in range(total_pages)]

        if len(self.pages) > 1:
            # Enter paged mode
            handler = TextWindowPagingEventHandler(self.engine)
            self.engine.event_handler = handler 

    def render(self,console:Console):
        """ Render the current page of messages.  
        """
        if len(self.pages) == 0:
            return
        page = self.pages[self.current_page]

        # TODO scrolling up/down
        lines_to_print = page[-self.height:]

        if len(self.pages) > 1 and self.current_page < len(self.pages) - 1:
            lines_to_print.append(("    -- More --",colors.ui_fg))

        for i,(text,color) in enumerate(lines_to_print):
            console.print(x=self.x,y=self.y+i,string=text,fg=colors.ui_fg)
            
            



