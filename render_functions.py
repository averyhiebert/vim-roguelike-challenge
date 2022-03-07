from __future__ import annotations

from typing import TYPE_CHECKING

import colors

def render_bar(console:Console,map_dims:Tuple[int,int],
        current_value:int, maximum_value:int, total_width:int) -> None:
    map_width, map_height = map_dims

    bar_width = int(current_value/maximum_value * total_width)

    console.draw_rect(x=0,y=map_height,width=total_width,height=1,ch=1,
        bg=colors.bar_empty)
    if bar_width > 0:
        console.draw_rect(x=0,y=map_height,width=bar_width,height=1,ch=1,
            bg=colors.bar_filled)
    #console.print(x=0+total_width+1, y=map_height,
    console.print(x=1, y=map_height,
        string=f"HP: {current_value}/{maximum_value}",fg=colors.ui_fg)
