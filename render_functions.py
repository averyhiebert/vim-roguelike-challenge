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
    fg = colors.ui_fg
    # TODO Not sure if I actually like the box outline.
    """
    console.draw_frame(x=51,y=0,
        width=24,height=15,
        decoration="/-\| |\-/",
        fg=colors.ui_fg
    )
    """
    # TODO Dungeon level number?
    render_bar(console,(51,13),health,max_health,total_width=22)
    console.print(51,1,string=level_name,fg=fg)
    console.print(51,2,string=22*"-",fg=fg)
    console.print(51,3,string=f"Gold     : {gold}",fg=fg)
    console.print(51,4,string=f"Range    : {max_range}",fg=fg)
    console.print(51,5,string=f"Armour   : {AC}",fg=fg)
    console.print(51,6,string=f"Strength : {strength}",fg=fg)
    console.print(51,7,string=f"Abilities:",fg=fg)
    ability_str = "\n".join(textwrap.wrap(
        abilities,width=22,
        initial_indent="  ",subsequent_indent="  ")
    )
    console.print(51,8,string=ability_str,fg=fg)
    console.print(51,14,string=22*"-",fg=fg)

    # Left bar
    console.ch[49,0:38] = ord("~")
    console.fg[49,0:38] = colors.medium_blue

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

def render_main_menu(console:Console):
    """ Render a main menu screen. """

    console.print(0,5,string="VimRC - Vim Roguelike Challenge".center(75)
        ,fg=colors.ui_fg)
    console.print(0,7,string="version 0.1.0".center(75),
        fg=colors.ui_fg)
    console.print(0,8,string="by Avery Hiebert".center(75),
        fg=colors.ui_fg)
    console.print(0,9,string="VimRC is open source and freely distributable".center(75),
        fg=colors.ui_fg)

    console.print(0,13,string="Choose your starting class:".center(75),
        fg=colors.ui_fg)

    subwidth = 15
    console.print(0,17,string=f"f: {'fighter':<15}{'(recommended)':<21}".center(75),fg=colors.ui_fg)
    console.print(0,18,string=f"r: {'ranger':<15}{'(recommended)':<21}".center(75),fg=colors.ui_fg)
    console.print(0,20,string=f"c: {'chaos wizard':<15}{'':21}".center(75),fg=colors.ui_fg)
    console.print(0,21,string=f"p: {'pacifist':<15}{'':<21}".center(75),fg=colors.ui_fg)
    console.print(0,22,string=f"s: {'sapper':<15}{'':<21}".center(75),fg=colors.ui_fg)

    console.print(0,24,string=f"v: {'vimtutor':<15}{'(access all commands)':<21}".center(75),fg=colors.ui_fg)


    # Left bar
    console.ch[0,0:40] = ord("~")
    console.fg[0,0:40] = colors.medium_blue
