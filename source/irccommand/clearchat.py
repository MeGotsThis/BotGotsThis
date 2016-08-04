import bot.config
from bot import data
from typing import Optional


def parse(chat: 'Optional[data.Channel]',
          nick: Optional[str]):
    if nick == bot.config.botnick and isinstance(chat, data.Channel):
        chat.isMod = False
        chat.clear()
