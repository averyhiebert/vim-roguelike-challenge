# TODO Pick a palette in a more principled manner


test_bg = (0,80,0)  # Useful for testing stuff

# Basic tile colours (for fov/lighting stuff)
default_bg = (0,0,0)        # Used by default in background
default_FOV_bg = (25,25,25) # Used by default in background where visible
default_dim_fg = (200,200,200) # Might use for fg when not in FOV, maybe?
default_fg = (255,255,255)  # Used by default for foreground colour

# Etity colours
player = default_fg
ed = (200,120,0)
sed = ed
nano = (0,255,255)
gedit = nano
emacs = (255,50,50)
needle = (200,0,0)
vimic = needle
vimpire = needle

# Items
amulet = default_fg 
equipment = default_fg
scroll = default_fg

# Map trace colours
default_trace = (0,100,100) # A fairly neutral faint teal
move_trace = (0,100,100)    # To be used when moving
delete_trace = (100,0,0)    # To be used when deleting/attacking
yank_trace = (0,100,0)      # To be used when yanking
highlight = (100,100,0)     # For hlsearch (within FOV)
highlight_dark = (50,50,0)     # For hlsearch (outside of FOV)

# UI

ui_fg = (255,255,255)   # Plain light colour, presumably white
bar_filled = (50,100,50)
bar_empty = (50,50,50)

error_fg = (255,255,255)
error_bg = (255,0,0) # Mimics vim error text, may change though.

