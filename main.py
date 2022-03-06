''' A roguelike based on vim. '''
import copy

import tcod

from engine import Engine
import entity_factories
from procgen import generate_dungeon
from input_handlers import EventHandler

def main() -> None:
    screen_width = 70
    screen_height = 40

    map_width = 60
    map_height = 40

    tileset = tcod.tileset.load_tilesheet("images/dejavu_wide16x16_gs_tc.png",32,8,
        tcod.tileset.CHARMAP_TCOD)

    event_handler = EventHandler()

    player = copy.deepcopy(entity_factories.player)

    game_map = generate_dungeon(map_width, map_height,player)

    engine = Engine(event_handler=event_handler,
         game_map=game_map, player=player)

    with tcod.context.new_terminal(screen_width,screen_height,
            tileset=tileset,title="Vim Roguelike Challenge (VimRC)",
            vsync=True) as context:
        root_console = tcod.Console(screen_width,screen_height,order="F")
        while True:
            engine.render(console=root_console,context=context)

            events = tcod.event.wait()

            engine.handle_events(events)


if __name__=="__main__":
    main()
