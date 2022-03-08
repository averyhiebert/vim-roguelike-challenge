''' A roguelike based on vim. '''
import copy
import traceback

import tcod

import colors
from engine import Engine
import entity_factories
from procgen import generate_dungeon

def main() -> None:
    screen_width = 75
    screen_height = 40

    map_width = screen_width - 25
    map_height = screen_height - 2

    tileset = tcod.tileset.load_tilesheet("images/dejavu_wide16x16_gs_tc.png",32,8,
        tcod.tileset.CHARMAP_TCOD)


    player = copy.deepcopy(entity_factories.player)

    engine = Engine(player=player)
    engine.game_map = generate_dungeon(map_width, map_height,engine=engine)
    engine.update_fov()

    engine.message_log.add_message(
        "Welcome to the Vim Roguelike Challenge (VimRC)."
    )


    with tcod.context.new_terminal(screen_width,screen_height,
            tileset=tileset,title="Vim Roguelike Challenge (VimRC)",
            vsync=True) as context:
        root_console = tcod.Console(screen_width,screen_height,order="F")
        while True:
            try:
                engine.render(console=root_console,context=context)
                engine.event_handler.handle_events()
            except Exception as err:
                # TODO Do this in a way that doesn't risk the entire program
                #  freezing if there's an error in the rendering or something.
                traceback.print_exc()
                engine.message_log.add_message(str(err))


if __name__=="__main__":
    main()
