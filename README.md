# VimRC - Vim Roguelike Challenge 

The roguelike you just can't quit!

An old-school ascii-based dungeon crawler mechanically & thematically inspired by the best text editor, vim.  Explore dungeons using powerful navigation commands, yank loot, and delete enemies like the enigmatic `ed` and the dreaded `Emacs` in your quest to retrieve the Amulet of Yendor.

[Download for linux & windows here!](https://averyhiebert.itch.io/vim-roguelike-challenge)

## Why?

Vim and classic roguelikes have a lot in common - a text based interface, steep learning curve, great potential for mastery, items/commands that combine in powerful ways, and a history of free and open source software.  So why not combine the two?  Being half-decent at vim make me feel like a powerful text editing wizard, so I thought it might be fun to try and carry that feeling over to a video game, and the 7 Day Roguelike Challenge presented the perfect opportunity.

## Controls

For more detailed instructions, see [the documentation](docs/README.md).

Basically, I tried my best to implement vim movement in a roguelike context. Use `hjkl` (or arrow keys, if you insist) to move, `d`+movement to attack, `yy` to pick up items at your current location, `"rp` to drop the item in register `r`, and `@r` to use/consume the item in register `r`.

Consult the "cursor movement" section of a [vim cheat sheet](https://vim.rtorr.com/) for a wide range of additional options. Not all commands are implemented, but many are (with some natural modifications to suit gameplay). However, they will generally require an amulet to use. Try out the "vimtutor" starting class to experiment with all available commands.

VimRC is self-documenting in the form of a `:help` command.  For instance, to learn about controls try `:help controls`.


## License

Just for fun, in addition to the MIT license this project is also available under the vim license (i.e. you may use/distribute it under the terms of either of these licenses, at your discretion). Hopefully this doesn't cause some sort of headache in the future.


## About

Made for the 7 Day Roguelike Challenge.  Engine architecture largely copied from [this tutorial,](https://rogueliketutorials.com/tutorials/tcod/v2/) to which I am deeply indebted.
