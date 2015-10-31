from bot import globals

def whisper(nick):
    return lambda m, p=1: globals.messaging.queueWhisper(nick, m, p)

def channel(channel):
    return channel.sendMessage
