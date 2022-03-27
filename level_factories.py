from procgen import BasicDungeon, TestDungeon, TutorialDungeon

# Reminder: map size is 50,38

# TODO: varying enemy spawn rate for some rooms.
#  (Maybe easiest to just make it a multiplicative factor on the base rate)

default= BasicDungeon("Dungeon")
tunnels = BasicDungeon("TCP Tunnels",
        room_size_range=((4,4),(4,4)),
        max_rooms=30,
        allow_overlap=True)
mines = BasicDungeon("GNOMEish Mines", # Probably good for lower levels
        room_size_range=((4,4),(4,4)),
        max_rooms=30,
        diagonal=True,
        allow_overlap=True)
bigrooms = BasicDungeon("Dungeon",
        room_size_range=((9,14),(9,14)), # Maybe should bigger + more monsters?
        max_rooms=4,
        allow_overlap=True)
# TODO Make a better cellar, or remove this
cellar = BasicDungeon("Standard Library", 
        room_size_range=((30,48),(6,6)),
        max_rooms=100) # Need to try real hard
cellar_vertical = BasicDungeon("Standard Library",
        room_size_range=((6,6),(25,36)),
        max_rooms=100)
# TODO Should have more monsters than usual
# TODO Maybe hide something inside one of the solid blocks
great_hall = BasicDungeon("/dev/null",
        room_size_range=((4,4),(4,5)),
        invert=True,
        do_tunnels=False,
        max_rooms=15)
# TODO Goes below the lowest level, as a trap/bonus once you have AoY
# TODO Should have more items than usual.
disconnected = BasicDungeon("Treasury",
        invert=False,
        do_tunnels=False,
        max_rooms=50)

# The tutorial level
tutorial = TutorialDungeon("Tutorial")
