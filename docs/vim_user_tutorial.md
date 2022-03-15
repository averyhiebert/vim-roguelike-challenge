# VimRC Tutorial (for vim users)

I've tried to make the controls for this game as vim-like as possible given the timeframe and genre, but obviously it can't match perfectly 1-to-1 with vim.

This document summarizes the differences between VimRC commands and vim
commands, and the basic gameplay mechanics (inventory, "observe" mode, and
using items).  For information about enemy types, items, etc. use the built-in
`:help` documentation.

## Movement

Most basic movement commands are implemented, but aside from `hjkl` they
typically require an amulet (e.g. you can't use `f` until you have an `amulet
of f`).  If you want to experiment and find out which commands are supported, try out the `vimtutor` starting class.

For the purposes of `w` and `e`, a "word" is an alphabetic character (which
always represents an enemy).  Commands `t` and `w` move you adjacent to a
target, while `f` and `e` will move you directly to the target tile if possible,
or to the other side of the tile if the tile is occupied.

Although regex search exists, you cannot currently move to the next search result using `n`.  Sorry.

### Range

The player has a maximum "range," which is the largest number that you are
allowed to use in a command. E.g. if you tried the command `99l` while only
having a range of 5, it would be interpreted as the command `5l` instead. You
can upgrade your range for 10 gold using `upgrade range`.

## Attacking/Deleting

Deleting (attacking) is performed with `d` + a movement command, as you would
expect.  This moves the player as well as attacking anything in the path of
the movement. However, if the player has a ranged weapon equipped, they will
not move when deleting.  I suppose it's philosophically debatable which of
these two cases matches the usual behaviour of vim.

## Yanking/putting/registers (inventory)

Yanking is performed with `y` + a movement command.  `yy` will yank everything on the tile underneath the player.  Items will be inserted into available registers in alphabetical order. If you specify a register (e.g. `"ayy`) then
the first item yanked will be put in that register.

You can put (drop) an item using p. If no register is specified, the most recently-yanked-into register will be used.

Use `i` to view your inventory.  (You can also use `:registers` or `:reg`
if you find that more intuitive). Numbered registers are considered to be "equipped" while alphabetic registers are unequipped. Use `:swap a b` to swap the contents of registers `a` and `b`.

Deleting does not automatically yank, unless a magnet is equipped.

## Using items/macros

Type `@r` to use/consume the item in register `r`. This is analogous to macros. Unfortunately, I didn't have time to implement macros

## "Observing"

Use `o` to "observe" the contents of a tile. Pressing `o` will enter "observe"
mode.  Move the cursor to the tile of interest, and press `o` again (or enter).

## Searching

You can do a regex search with `/` or `?` as expected. This does nothing unless you have already `:set hlsearch`, which will typically require a scroll
(except in vimtutor mode).  This uses python regex syntax, rather than vim regex syntax (sorry).

## Commands
Most vim commands are not implemented.  A couple `:s` commands are available as single-use scrolls. In addition, there are several game-specific commands:

`:upgrade [range|strength|armour]` will upgrade stats (for 10 gold).
`:new` starts a new game.
`:q`,`:wq`, and `:q!` function as expected.

There is built-in documentation for most things using `:help [keyword]`, as expected.
