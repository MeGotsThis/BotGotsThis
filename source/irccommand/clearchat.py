from bot import config


def parse(chat, nick):
    if nick == config.botnick:
        chat.isMod = False
        chat.socket.messaging.clearChat(chat.channel)
