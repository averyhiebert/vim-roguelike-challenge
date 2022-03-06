from __future__ import annotations

from typing import Optional
from typing import Optional, TYPE_CHECKING

import tcod.event

from actions import Action, BumpAction, EscapeAction

if TYPE_CHECKING:
    from engine import Engine

class EventHandler(tcod.event.EventDispatch[Action]):
    def __init__(self, engine:Engine):
        self.engine = engine

    def handle_events(self) -> None:
        for event in tcod.event.wait():
            action = self.dispatch(event)

            if action is None:
                continue

            action.perform()

            self.engine.handle_enemy_turns()
            self.engine.update_fov() # Update FOV before player's next turn

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        key = event.sym

        player = self.engine.player

        if key in [tcod.event.K_UP]:
            action = BumpAction(player, (0,-1))
        elif key in [tcod.event.K_DOWN]:
            action = BumpAction(player, (0,1))
        elif key in [tcod.event.K_LEFT]:
            action = BumpAction(player, (-1,0))
        elif key in [tcod.event.K_RIGHT]:
            action = BumpAction(player, (1,0))

        elif key == tcod.event.K_ESCAPE:
            action = EscapeAction(player)

        return action
