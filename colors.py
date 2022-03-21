# TODO Pick a palette in a more principled manner

# "slate" colour scheme from vim
black = (0,0,0)
dark = (0x26,0x26,0x26)
off_dark = (0x2a,0x2a,0x2a)
medium = (0x32,0x48,0x5e)

light_red = (0xff,0x8a,0x5c)
red = (0xff,0x00,0x07)

white = (0xff,0xff,0xce)
beige = (0xff,0xde,0x95)
yellow = (0xf0,0xd7,0x00)
orange = (0xda,0xa5,0x20)

light_blue = (0x87,0xce,0xc7)
medium_blue = (0x64,0x95,0xed)

green = (0x00,0x80,0x00)
light_green = (0x6b,0x8e,0x23)


test_bg = (0,80,0)  # Useful for testing stuff

# Basic tile colours (for fov/lighting stuff)
default_bg = dark       # Used by default in background
default_FOV_bg = off_dark # Used by default in background where visible
default_dim_fg = beige # Might use for fg when not in FOV, maybe?
default_fg = white  # Used by default for foreground colour

# Specific tile colors
water_fg = medium_blue
water_dim_fg = medium_blue

# Entity colours
player = default_fg
ed = orange 
sed = ed
#nano = yellow
nano = medium_blue
gedit = nano
emacs = red
needle = light_red
vimic = needle
vimpire = red

# Items
amulet = default_fg 
equipment = default_fg
scroll = default_fg
gold = yellow 

# Map trace colours
default_trace = light_blue # A fairly neutral faint teal
move_trace = light_blue    # To be used when moving
delete_trace = red    # To be used when deleting/attacking
explosion_trace=orange # For explosions
yank_trace = green      # To be used when yanking
highlight = medium     # For hlsearch (within FOV)
highlight_dark = medium     # For hlsearch (outside of FOV)

# UI
ui_fg = beige   # Plain light colour, presumably white
bar_filled = green
bar_empty = medium 

# Message log

important = light_blue
normal = beige
bad = light_red
very_bad = red

# Status bar
error_fg = white 
error_bg = red # Mimics vim error text, may change though.
tutorial_fg = white 
tutorial_bg = green

