from typing import Optional

import tcod.event

from actions import Action, BumpAction, EscapeAction

class EventHandler(tcod.event.EventDispatch[Action]):
    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        key = event.sym

        if key in [tcod.event.K_UP]:
            action = BumpAction((0,-1))
        elif key in [tcod.event.K_DOWN]:
            action = BumpAction((0,1))
        elif key in [tcod.event.K_LEFT]:
            action = BumpAction((-1,0))
        elif key in [tcod.event.K_RIGHT]:
            action = BumpAction((1,0))

        elif key == tcod.event.K_ESCAPE:
            action = EscapeAction()

        return action
