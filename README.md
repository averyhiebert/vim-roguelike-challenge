# VimRC - Vim Roguelike Challenge 

The roguelike you just can't quit!

An old-school roguelike inspired by the superior text editor.  Explore dungeons using powerful navigation commands, yank loot, and delete enemies like the enigmatic `ed` and the dreaded `Emacs` in your quest to retrieve the Amulet of Yendor. 

## Controls

Basically, most movement commands from vim will also work. Use `hjkl` (or arrow keys, if you insist) to move, `d`+movement to attack, `yy` to pick up items at your current location, and `"rp` to drop the item in register `r`.

Consult the "cursor movement" section of a [vim cheat sheet](https://vim.rtorr.com/) for more info. Not all commands are implemented, but many are (with some natural modifications to suit gameplay). However, they will generally require an amulet to use. Try out the "vimtutor" starting class to experiment with all available commands.

VimRC is self-documenting in the form of a `:help` command.  For instance, to learn about controls try `:help controls`.  A text version of the documentation that you can browse through, as well as a summary of differences intended specifically for vim users, is in the works. 

## License

Just for fun, in addition to the MIT license this project is also available under the vim license (i.e. you may use/distribute it under the terms of either of these licenses, at your discretion). Hopefully this doesn't cause some sort of headach in the future.


## About

Made for the 7 Day Roguelike Challenge.  Engine architecture largely copied from [this tutorial,](https://rogueliketutorials.com/tutorials/tcod/v2/) to which I am deeply indebted.
