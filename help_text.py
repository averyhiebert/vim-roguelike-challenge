# TODO Figure out why there's a bunch of stuff I can't import from entity_factories
#  Presumably some sort of circular dependency? TODO Find a way to solve this.

help_text = {
    "quit": "Type :wq to save and quit, or :q! to quit without saving.",
    "help": "You already know what the help command does :)",
    # TODO Vim user summary
    # General queries
    "winning":"To win, descend to the bottom of the dungeon (don't overshoot!), find the Amulet of Yendor, and return to the Altar of Victory in the top level with the amulet equipped.",
    "drop":"Use p (put) to drop objects. \"rp will drop the item in register r.",
    "grab":"Use y (yank) to obtain objects. \"ry[movement command] will yank all items along the path that the player WOULD travel if just [movement command] was performed, and the first item yanked will be placed in register r.",
    "movement":"Use hjkl or arrow keys to move (except for starting class Chaos Wizard).  These can be modified by numbers (e.g. 3l will move right three times) and by d or y (to delete and/or yank instead of (just) moving). In addition, many other vim movement commands are supported, although they generally require an amulet or class ability.\nEach individual *keystroke* takes a turn (with exceptions, see help: turns), so be strategic.\nFor more information, consult a vim tutorial or cheat sheet.",
    "controls":"Use hjkl or arrow keys to move (except for starting class Chaos Wizard).  These can be modified by numbers (e.g. 3l will move right three times) and by d or y (to delete and/or yank instead of (just) moving). In addition, many other vim movement commands are supported, although they generally require an amulet or class ability.\nEach individual *keystroke* takes a turn (with exceptions, see help: turns), so be strategic.\nFor more information, consult a vim tutorial or cheat sheet.\n(For information about other actions see :help delete, :help yank, :help put, :help look, :help use)",
    "turns":"In general, each keystroke takes one turn, and commands beginning with a colon do not take a turn.\nExceptions: specifying a register before a yank, put, or delete command does not take a turn, and the commands :swap and :upgrade do expend a turn.",
    "attack":"Use d followed by any movement command to move as instructed *and* attack any enemies encountered along the way.  Exception: if you have a ranged weapon equipped you will not move when attacking.",
    "inventory":"Use i to view your inventory.\nWhen yanking (picking up) or putting (dropping) an object, you can specify a register r by typing \"r at the beginning of the command.  Specifying a register does not take any in-game turns.\nYou can swap registers x and y using the command `:swap x y`, which *does* take a turn.",
    "look":"Press o to look at a tile in detail. Pressing o once will enter cursor movement mode, and pressing o a second time (or enter) will look at the selected tile. This does not take an in-game turn.",
    "use":"Type @r to use/consume the item in register r.",
    "upgrade":"You can upgrade strength, armour, or range for 10 gold using the command `:upgrade [insert stat here]`. This costs 10 gold.",
    "search":"You can perform a regex search using / or ?, as expected in vim.  However, this only has an effect if hlsearch has been turned on (using a scroll of `:set hlsearch`).",
    "macros":"Macros have not been implemented yet. Sorry to disappoint you.",
    "stairs":"Use > to descend stairs, or < to ascend.",

# Explain stats
    "health":"Health is lost when being attacked by enemies, and can be recovered by consuming corpses.",
    "hp":"Health is lost when being attacked by enemies, and can be recovered by consuming corpses.",
    "strength":"How much damage you deal when attacking.\nUpgrade for 10 gold with :upgrade strength.",
    "armour":"Provides resistance to attacks.  Damage less than your armour class is halved, and damage less than a quarter of your armour class is avoided entirely.\nUpgrade for 10 gold with :upgrade armour",
    "range":"The maximum number you can use in a movement command.  For example, if your range is 5 then the command d9l would be interpreted as d5l.\nUpgrade for 10 gold with :upgrade armour",
    "gold":"Gold can be spent on stat upgrades (see :help upgrade).",
    "abilities":"Typically granted by an equipped item, abilities allow you to perform various commands or modify the effect of other commands.\nAll classes of character start with some intrinsic abilities, in addition to any subsequently obtained.",

    # Abilities
    "ranged":"Players with the 'ranged' ability will not move when attacking using d",
    "magnetic":"Magnetic players vill automatically yank any items on squares covered by a movement or delete command.",
    "echolocate":"Allows you to move to unexplored/unseen characters with the t and f commands.",
    "H":"Move to top of map.",
    "M":"Move to middle of map.",
    "0":"Move to start of line (left side of map)",
    "$":"Move to end of line (right side of map)",
    "d":"Delete (i.e. attack).  Deleting also moves the player, unless you have a ranged weapon equipped.",
    "dd":"Attack the entire current line.",
    "y":"Yank (i.e. pick up objects). \"ryy will yank into register r",
    "yy":"Yank all items on the current square.",
    "p":"Put (i.e. drop objects). \"ryy will yank into register r",
    "h":"Move left.",
    "j":"Move down.",
    "k":"Move k.",
    "l":"Move right.",
    "'":"'a will move to the spot previously marked using command ma\n(where a could be replaced with any lowercase alphabetic character)",
    "`":"`a will move to the spot previously marked using command ma\n(where a could be replaced with any lowercase alphabetic character)",
    "m":"ma will mark a spot that can be returned to with `a\n(where a can be replaced with any lowercase alphabetic character)",
    "t":"t[character] will move to be adjacent to the nearest visible instance of the specified character.",
    "f":"f[character] will move directly to the nearest visible instance of the specified character, or to the far side of said character if the space is occupied.",
    "e":"f[character] will move directly to the nearest alphabetic character, or to the far side of said character if the space is occupied.",
    "w":"f[character] will move to be adjacent to the nearest alphabetic character, or to the far side of said character if the space is occupied.",
    ";":"Repeat the most recent t or f command.",
    "u":"Undo the results of the previous movement (i.e. move back to where you were previously).\nThis does not undo damage, yanking, etc.",
    "hlsearch":"When turned on, causes the results of a regex search to be highlighted on the map.",

    # Items
    # TODO Make this automatic in the future maybe
    "amulet":"An item that grants access to a certain ability when equipped.",
    "scroll":"A single-use item that executes a command when consumed.",
    "crossbow":"Enables the ranged ability when equipped (see :help ranged)",
    "bat ears":"Enables echolocation when equipped (see :help echolocate)",
    "magnet":"Makes the player magnetic when equipped (see :help echolocate)",
    "landmine":"Explodes after you step off it, dealing 15 damage that bypasses armour.",
    "altar":"Return to the altar with the Amulet of Yendor equipped to appease the gods and win the text editor holy war.",

    # Enemies
    # TODO Make this automatic as well
    "nano":"A hostile but weak text editor.\n2 hp, 2 strength",
    "ed":"ed is the standard text editor.\n3 hp, 3 strength",
    "sed":"A feral stream editor.\n2 hp, 2 strength",
    "gedit":"A feral stream editor.\n6 hp, 5 strength",
    "magnetized needle":"REAL programmers edit files using a magnetized needle and a steady hand (see xkcd#378). \n4 hp, 8 strength",
    "vimic":"A monster that mimics the features of vim. 15 hp, 10 strength",
    "vimpire":"A vile, corrupted vim-like entity. 20 hp, 12 strength",
    "emacs":"A lumbering monstrosity created by mad scientists. 30 hp, 15 strength",
    "emax":"Like Emacs, but moreso. 50 hp, 20 strength",
}


# Maps from a command not listed in help_text to one that *is* listed
synonyms = {
    "armor":"armour",
    "ac":"armour",
    "get":"grab",
    "yank":"grab",
    "put":"drop",
    "delete":"attack",
    "controls":"movement",
    "/":"search",
    "?":"search",
    "eat":"use",
    "consume":"use",
    "regex":"search",
    "q":"macros",
    "macro":"macros",
    "exit":"quit",
    "undo":"u",
    "mark":"m",
    ">":"stairs",
    "<":"stairs",
    "goal":"winning",
    "victory":"winning",
    "objective":"winning",
    "aim":"winning",
    "needle":"magnetized needle",
    "altar of victory":"altar",
    "amulet of yendor":"altar",
    "o":"look",
    "observe":"look",
}
