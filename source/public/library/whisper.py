import functools
from bot import utils
from . import chat


def send(nick):
    return functools.partial(utils.whisper, nick)

permission = chat.permission
not_permission = chat.not_permission
min_args = chat.min_args
