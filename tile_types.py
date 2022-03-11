from typing import Tuple

import numpy as np #type: ignore

import colors

# Tile graphics structured type compatible with Console.tiles_rgb
graphic_dt = np.dtype(
    [("ch",np.int32), # Unicode codepoint,
     ("fg", "3B"),    # 3 unsigned bytes, for RGB colors
     ("bg","3B"),
    ]
)

# Tile struct used for statically defined tile data.
# (First notable departure from tutorial: I still plan to draw unseen tiles,
#  albeit black on black, because I want to use the character data from the
#  console for some git commands. Maybe there's a nicer way to do this, but
#  I'm too lazy to think about it atm.)
tile_dt = np.dtype(
    [("walkable",np.bool),    # True if can be walked over
     ("transparent",np.bool), # True if can be seen through
     ("dark",graphic_dt),     # graphics for when not in FOV
     ("light",graphic_dt),    # graphics for when in FOV
     ("unseen",graphic_dt),   # graphics for when unexplored
     ("name_index",np.int32), # index into list of tile names
    ]
)

def new_tile(
        *, # Enforce use of keywords
        walkable: int, transparent: int,
        dark: Tuple[int,Tuple[int,int,int],Tuple[int,int,int]],
        light: Tuple[int,Tuple[int,int,int],Tuple[int,int,int]],
        name:str,
        ) -> np.ndarray:
    # Automatically generate the "unseen" graphic
    """Helper for defining individual tile types."""
    unseen = (dark[0],colors.default_bg,colors.default_bg)
    # Possibly useful when designing UI (makes map boundary visible):
    #unseen = (dark[0],colors.test_bg,colors.test_bg)
    return np.array((walkable,transparent,dark,light,unseen,name),dtype=tile_dt)

# Define tiles here =========================
tile_names = [
    "floor",
    "wall",
    "stairs (down)",
    "stairs (up)",
]
floor = new_tile(
    walkable=True, transparent=True,
    dark=(ord(" "),colors.default_dim_fg,colors.default_bg),
    light=(ord(" "),colors.default_fg,colors.default_FOV_bg),
    name=tile_names.index("floor"),
)
wall = new_tile(
    walkable=False, transparent=False,
    dark=(ord("#"),colors.default_dim_fg,colors.default_bg),
    light=(ord("#"),colors.default_fg,colors.default_FOV_bg),
    name=tile_names.index("wall"),
)
down_stairs = new_tile(
    walkable=True, transparent=True,
    dark=(ord(">"),colors.default_dim_fg,colors.default_bg),
    light=(ord(">"),colors.default_fg,colors.default_FOV_bg),
    name=tile_names.index("stairs (down)"),
)
up_stairs = new_tile(
    walkable=True, transparent=True,
    dark=(ord("<"),colors.default_dim_fg,colors.default_bg),
    light=(ord("<"),colors.default_fg,colors.default_FOV_bg),
    name=tile_names.index("stairs (up)"),
)
tile_names = np.array(tile_names) # To support fancy indexing
