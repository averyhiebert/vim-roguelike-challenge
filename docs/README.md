# Vim Roguelike Challenge Documentation

## For vim users:

Please see the [tutorial for vim users.](vim_user_tutorial.md)

Non-vim-users, please continue.

## Movement

Use `hjkl` to move left, down, up, and right respectively. Typing a number
before one of these letters (e.g. `5l`) will move you by that many spaces (up
to a limit, called your "range", which depends on your starting class and can
be upgraded).  This is important, as you will probably be unable to escape
enemies if you don't use this feature.

Consult the "cursor movement" section of a [vim cheat sheet](https://vim.rtorr.com/) for a wide range of additional options. Not all commands are implemented, but many are (with some natural modifications to suit gameplay). However, they will generally require an amulet to use. Try out the "vimtutor" starting class to experiment with all available commands.

## Attacking

Attack enemies by "deleting," i.e. typing `d` + a movement command.  For
instance, `d5l` will move right by 5 spaces *and* attack any enemies along
the way.

## Items

Pick up items by "yanking" with `y` + a movement command.  For instance, `y5l` will pick up any items up to 5 tiles to the right. `yy` will pick up any items on the tile currently occupied by the player.  When you pick up an item, it will be placed into a "register" identified by a letter or number.  Numbered registers are considered to be "equipped" while alphabetic registers are not.  You can view the contents of your registers by typing `i`.

You can use the item in register `r` by typing `@r`. This is how you consume
corpses (to recover HP) or activate scrolls.

## Quitting

To quit, use the command `:wq`.

## More

For more information, read the [tutorial for vim users.](vim_user_tutorial.md)
