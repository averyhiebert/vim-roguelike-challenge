from __future__ import annotations

from typing import Iterable, List, Reversible, Tuple, TYPE_CHECKING
import textwrap
import itertools

import tcod

import colors

if TYPE_CHECKING:
    from text_window import TextWindow

class Message:
    def __init__(self, text:str, fg:Tuple[int,int,int]):
        self.plain_text = text
        self.fg = fg
        self.count = 1

    @property
    def full_text(self) -> str:
        """The full text of this message, including the count if necessary."""
        if self.count > 1:
            return f"{self.plain_text} (x{self.count})\n"
        return f"{self.plain_text}\n"

class MessageLog:
    def __init__(self,text_window:TextWindow) -> None:
        self.text_window = text_window
        self.messages:List[Message] = []
        self.max_show_history = 100

    def add_message(self, text:str, fg:Tuple[int,int,int]=colors.ui_fg,
            *,stack: bool=True):
        """Add a message to this log.
        `text` is the message text, `fg` is the text color.
        If `stack` is True then the message can stack with a previous
        message of the same text.
        """
        if stack and self.messages and text == self.messages[-1].plain_text:
            self.messages[-1].count += 1
        else:
            self.messages.append(Message("",fg))
            self.messages.append(Message(text,fg))
        # Display self (i.e. replacing whatever was previously in the
        #  text window.
        self.display()

    def display(self) -> None:
        """Show this log in the text window."""

        # Only send a max number of messages to the textbox
        #  Note: we reverse so as to slice the last however-many, and
        #  then reverse again to send them to text window in correct order.
        # Would it really be that bad to just slice the original list?
        #  Probably not, but this seemed like a good idea at the time.
        truncated_texts = [(m.full_text, m.fg) for m in itertools.islice(reversed(self.messages),self.max_show_history)]
        self.text_window.show(list(reversed(truncated_texts)),
            message_log_mode=True)
