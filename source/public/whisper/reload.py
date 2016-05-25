from ..library import reload, send
from bot import globals

def commandReload(args):
    reload.botReload(send.whisper(args.nick))
    return True

def commandReloadCommands(args):
    reload.botReloadCommands(send.whisper(args.nick))
    return True

def commandReloadConfig(args):
    reload.botReloadConfig(send.whisper(args.nick))
    return True
