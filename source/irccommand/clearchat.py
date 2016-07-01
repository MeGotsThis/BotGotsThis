from bot import config, data
from typing import Optional


def parse(chat: 'Optional[data.Channel]',
          nick: Optional[str]):
    if nick == config.botnick and isinstance(chat, data.Channel):
        chat.isMod = False
        chat.clear()
