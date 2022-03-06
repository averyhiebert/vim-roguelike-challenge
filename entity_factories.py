from entity import Entity
import colors

player = Entity(char="@",color=colors.default_fg,name="Player",
    summary="A daring rogue.",blocks_movement=True)

# Define enemy types here
nano = Entity(char="n",color=colors.default_fg,name="nano",
    summary="A harmless text editor.",blocks_movement=True)
ed = Entity(char="e",color=colors.default_fg,name="ed",
    summary="An ? known for ? and ?",blocks_movement=True)
