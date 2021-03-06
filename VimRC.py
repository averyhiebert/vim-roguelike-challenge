''' A roguelike based on vim. '''
import copy
import traceback
import sys
import os

import tcod

import colors
from engine import Engine
import entity_factories
from procgen import TestDungeon, BasicDungeon, TutorialDungeon
from game_world import GameWorld
import level_factories as lf
import exceptions

# Some constants for development
# TODO Change these before final build...
USE_TEST_ROOM = False
USE_TUTORIAL = False
ALWAYS_NEW_GAME = True

def new_game(tileset,screen_width:int=75,screen_height:int=40,use_tutorial=False) -> Engine:
    """ Return a new game object (i.e. an Engine).

    Note: due to hardcoded values in UI elements, please do not use
    non-default screen_width and screen_height
    """
    map_width = screen_width - 25
    map_height = screen_height - 2

    player = copy.deepcopy(entity_factories.player)

    engine = Engine(player=player,main_menu_mode=True)
    engine.game_world = GameWorld(
        engine=engine,
        map_width=map_width,
        map_height=map_height
    )

    if USE_TEST_ROOM:
        level_gen = TestDungeon("Test")
        engine.set_game_map(level_gen.generate((map_width,map_height),
            engine,difficulty=1)
        )
    elif use_tutorial:
        level_gen = TutorialDungeon("Tutorial")
        engine.set_game_map(level_gen.generate((map_width,map_height),
            engine,difficulty=1)
        )
    else:
        engine.game_world.next_floor()

    engine.update_fov()
    engine.message_log.add_message(
        "Welcome to the Vim Roguelike Challenge (VimRC)!"
    )
    return engine


# See:  https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile/44352931#44352931
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def main() -> None:
    screen_width = 75
    screen_height = 40

    image_path = resource_path("images/dejavu_wide16x16_gs_tc.png")
    tileset = tcod.tileset.load_tilesheet(image_path,
        32,8,tcod.tileset.CHARMAP_TCOD)
    #image_path = resource_path("images/dwarf_fortress.png")
    #tileset = tcod.tileset.load_tilesheet(image_path,
    #    16,16,tcod.tileset.CHARMAP_CP437)

    try:
        engine = Engine.load("vimrc.sav")
        assert(not ALWAYS_NEW_GAME)
    except:
        #Save file dow not exist, or we're in always-new testing mode.
        engine = new_game(
            tileset,
            screen_width=screen_width,
            screen_height=screen_height
        )

    # Note: the font is 16 by 16, but I request a 12:16 aspect ratio for
    #  the window it's displayed in, which more-or-less gives the effect of
    #  a reasonable 12x16 font.
    with tcod.context.new_terminal(int(0.75*screen_width),screen_height,
            tileset=tileset,title="Vim Roguelike Challenge (VimRC)",
            vsync=True) as context:
        root_console = tcod.Console(screen_width,screen_height,order="F")
        root_console.default_bg=colors.dark
        while True:
            try:
                engine.render(console=root_console,context=context)
                engine.event_handler.handle_events()
            except exceptions.UserError as err:
                engine.show_error_message(str(err))
            except exceptions.Impossible as err:
                engine.message_log.add_message(str(err))
            except NotImplementedError as err:
                traceback.print_exc()
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
                #raise err


if __name__=="__main__":
    main()
