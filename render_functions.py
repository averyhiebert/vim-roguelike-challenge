from __future__ import annotations

from typing import TYPE_CHECKING

import colors

def render_bar(console:Console,position:Tuple[int,int],
        current_value:int, maximum_value:int, total_width:int) -> None:
    #map_width, map_height = map_dims
    x,y = position

    bar_width = int(current_value/maximum_value * total_width)

    console.draw_rect(x=x,y=y,width=total_width,height=1,ch=1,
        bg=colors.bar_empty)
    if bar_width > 0:
        console.draw_rect(x=x,y=y,width=bar_width,height=1,ch=1,
            bg=colors.bar_filled)
    #console.print(x=0+total_width+1, y=map_height,
    console.print(x=x+1, y=y,
        string=f"HP: {current_value}/{maximum_value}",fg=colors.ui_fg)

def render_stat_box(console:Console,health:int,
        max_health:int,gold:int) -> None:
    console.draw_frame(x=51,y=0,
        width=24,height=15,
        decoration="/-\| |\-/",
        fg=colors.ui_fg
    )
    render_bar(console,(52,13),health,max_health,total_width=22)
