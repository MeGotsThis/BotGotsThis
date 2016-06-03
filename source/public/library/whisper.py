from . import chat
from bot import utils
from functools import partial, wraps

def send(nick):
    return functools.partial(utils.whisper, nick)

permission = chat.permission
not_permission = chat.not_permission
min_args = chat.min_args
