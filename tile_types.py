from typing import Tuple

import numpy as np #type: ignore

# Tile graphics structured type compatible with Console.tiles_rgb
graphic_dt = np.dtype(
    [("ch",np.int32), # Unicode codepoint,
     ("fg", "3B"),    # 3 unsigned bytes, for RGB colors
     ("bg","3B"),
    ]
)

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
    [("walkable",np.bool),    # True if can be walked over
     ("transparent",np.bool), # True if can be seen through
     ("dark",graphic_dt),     # graphics for when not in FOV
    ]
)

def new_tile(
        *, # Enforce use of keywords
        walkable: int, transparent: int,
        dark: Tuple[int,Tuple[int,int,int],Tuple[int,int,int]]) -> np.ndarray:
    """Helper for defining individual tile types."""
    return np.array((walkable,transparent,dark),dtype=tile_dt)

# Define tiles here =========================
floor = new_tile(
    walkable=True, transparent=True,dark=(ord(" "),(0,0,0),(0,0,0))
)
wall = new_tile(
    walkable=False, transparent=False,dark=(ord("#"),(255,255,255),(0,0,0))
)
