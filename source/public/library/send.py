from bot import utils
import functools

def whisper(nick):
    return functools.partial(utils.whisper, nick)

def channel(chat):
    return chat.sendMessage
