from procgen import BasicDungeon, TestDungeon

# Reminder: map size is 50,38

level_types = {
    "default":BasicDungeon("Dungeon"),
    "maze":BasicDungeon("Dungeon",
        room_size_range=((4,4),(4,4)),
        max_rooms=30,
        allow_overlap=True),
    "crisscross":BasicDungeon("Dungeon", # Probably good for lower levels
        room_size_range=((4,4),(4,4)),
        max_rooms=30,
        diagonal=True,
        allow_overlap=True),
    "bigrooms":BasicDungeon("Dungeon",
        room_size_range=((9,14),(9,14)), # Maybe should bigger + more monsters?
        max_rooms=4,
        allow_overlap=True),
    # TODO Make a better cellar
    "cellar":BasicDungeon("Dungeon",
        room_size_range=((30,48),(6,8)),
        max_rooms=30),
}
