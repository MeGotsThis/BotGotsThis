from bot.data import channel
from bot import config


def parse(chat: 'channel.Channel',
          nick: str):
    if nick == config.botnick:
        chat.isMod = False
        chat.socket.messaging.clearChat(chat)
