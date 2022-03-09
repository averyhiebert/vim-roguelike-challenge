''' A roguelike based on vim. '''
import copy
import traceback

import tcod

import colors
from engine import Engine
import entity_factories
from procgen import generate_dungeon
import exceptions

def new_game(tileset,screen_width:int=75,screen_height:int=40) -> Engine:
    """ Return a new game object (i.e. an Engine).

    Note: due to hardcoded values in UI elements, please do not use
    non-default screen_width and screen_height
    """
    map_width = screen_width - 25
    map_height = screen_height - 2



    player = copy.deepcopy(entity_factories.player)

    engine = Engine(player=player)
    engine.set_game_map(generate_dungeon(map_width, 
        map_height,engine=engine))
    engine.update_fov()

    engine.message_log.add_message(
        "Welcome to the Vim Roguelike Challenge (VimRC)."
    )
    return engine



def main() -> None:
    screen_width = 75
    screen_height = 40
    tileset = tcod.tileset.load_tilesheet("images/dejavu_wide16x16_gs_tc.png",32,8,
        tcod.tileset.CHARMAP_TCOD)

    try:
        engine = Engine.load("save.sav")
    except:
        engine = new_game(
            tileset,
            screen_width=screen_width,
            screen_height=screen_height
        )

    with tcod.context.new_terminal(screen_width,screen_height,
            tileset=tileset,title="Vim Roguelike Challenge (VimRC)",
            vsync=True) as context:
        root_console = tcod.Console(screen_width,screen_height,order="F")
        while True:
            try:
                engine.render(console=root_console,context=context)
                engine.event_handler.handle_events()
            except exceptions.UserError as err:
                # TODO Use the status bar, not message log.
                #engine.message_log.add_message(str(err))
                engine.show_error_message(str(err))
            except exceptions.Impossible as err:
                engine.message_log.add_message(str(err))
                #engine.show_error_message(str(err))
            except NotImplementedError as err:
                traceback.print_exc()
                #engine.message_log.add_message(str(err))
                engine.show_error_message(str(err))
            except exceptions.NewGame:
                # Trigger a new game.
                # I know this is bad, but I'm under time pressure here.
                engine = new_game(
                    tileset,
                    screen_width=screen_width,
                    screen_height=screen_height
                )
            except Exception as err:
                # TODO Do this in a way that doesn't risk the entire program
                #  freezing if there's an error in the rendering or something.
                traceback.print_exc()
                #engine.message_log.add_message(str(err))
                engine.show_error_message(str(err))
                # TEMP: While working on UI stuff:
                raise err


if __name__=="__main__":
    main()
