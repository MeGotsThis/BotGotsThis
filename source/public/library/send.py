from bot import globals
import functools

def whisper(nick):
    return functools.partial(globals.messaging.queueWhisper, nick)

def channel(chat):
    return chat.sendMessage
