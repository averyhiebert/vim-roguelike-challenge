from components.ai import HostileEnemy
from components.fighter import Fighter
from entity import Entity, Actor
import colors

player = Actor(
    char="@",
    color=colors.default_fg,
    name="player",
    summary="A daring rogue.",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=30,AC=10,to_hit="1d20",damage="1d20")
)

# Define enemy types here
nano = Actor(
    char="n",
    color=colors.nano,
    name="nano",
    summary="A harmless text editor.",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=8,AC=8,to_hit="1d20",damage="1d4")
)
ed = Actor(
    char="e",
    color=colors.ed,
    name="ed",
    summary="An ? known for ? and ?",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=8,AC=8,to_hit="1d12",damage="1d6")
)
