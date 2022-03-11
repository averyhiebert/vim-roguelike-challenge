from __future__ import annotations

from typing import TYPE_CHECKING
import textwrap

from entity import Actor

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

def render_stat_box(console:Console,
        level_name:str,
        health:int, max_health:int,
        gold:int,
        strength:int,
        max_range:int,
        AC:int,
        abilities:str) -> None:
    # TODO Not sure if I actually like the box outline.
    console.draw_frame(x=51,y=0,
        width=24,height=15,
        decoration="/-\| |\-/",
        fg=colors.ui_fg
    )
    # TODO Dungeon level number?
    render_bar(console,(52,13),health,max_health,total_width=22)
    console.print(52,1,string=level_name)
    console.print(52,2,string=22*"-")
    console.print(52,3,string=f"Gold     : {gold}")
    console.print(52,4,string=f"Range    : {max_range}")
    console.print(52,5,string=f"Armour   : {AC}")
    console.print(52,6,string=f"Strength : {strength}")
    console.print(52,7,string=f"Abilities:")
    # TODO Wrap abilities
    ability_str = "\n".join(textwrap.wrap(
        abilities,width=22,
        initial_indent="  ",subsequent_indent="  ")
    )
    console.print(52,8,string=ability_str)

def render_cursor(console:Console,position:Tuple[int,int],
        in_fov:bool):
    """ Render a cursor at given location.
    """
    if in_fov:
        console.fg[position] = colors.default_bg
        console.bg[position] = colors.ui_fg
    else:
        console.fg[position] = colors.ui_fg
        console.bg[position] = colors.ui_fg
