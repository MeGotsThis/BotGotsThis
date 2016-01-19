from bot import config, globals

def parse(chat, nick):
    if nick == config.botnick:
        chat.isMod = False
        globals.messaging.clearQueue(chat.channel)
