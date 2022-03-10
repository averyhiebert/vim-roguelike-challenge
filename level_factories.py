from procgen import BasicDungeon, TestDungeon

# Reminder: map size is 50,38

level_types = {
    "default":BasicDungeon("Dungeon"),
    "maze":BasicDungeon("Dungeon",
        room_size_range=((4,6),(4,6)),
        max_rooms=30),
    "bigrooms":BasicDungeon("Dungeon",
        room_size_range=((9,14),(9,14)),
        max_rooms=4,
        allow_overlap=True),
    "cellar":BasicDungeon("Dungeon",
        room_size_range=((30,48),(6,8)),
        max_rooms=30),
}
