from procgen import BasicDungeon, TestDungeon

# Reminder: map size is 50,38

# TODO: varying enemy spawn rate for some rooms.
#  (Maybe easiest to just make it a multiplicative factor on the base rate)

default= BasicDungeon("Dungeon")
maze = BasicDungeon("Dungeon",
        room_size_range=((4,4),(4,4)),
        max_rooms=30,
        allow_overlap=True)
crisscross = BasicDungeon("Dungeon", # Probably good for lower levels
        room_size_range=((4,4),(4,4)),
        max_rooms=30,
        diagonal=True,
        allow_overlap=True)
bigrooms = BasicDungeon("Dungeon",
        room_size_range=((9,14),(9,14)), # Maybe should bigger + more monsters?
        max_rooms=4,
        allow_overlap=True)
# TODO Make a better cellar, or remove this
cellar = BasicDungeon("Dungeon",
        room_size_range=((30,48),(6,8)),
        max_rooms=30)
# TODO Should have more monsters than usual
great_hall = BasicDungeon("Dungeon",
        room_size_range=((4,4),(4,5)),
        invert=True,
        do_tunnels=False,
        max_rooms=15)
# TODO Goes below the lowest level, as a trap/bonus once you have AoY
# TODO Should have more items than usual.
disconnected = BasicDungeon("Dungeon",
        invert=False,
        do_tunnels=False,
        max_rooms=40)
