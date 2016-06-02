from ..library import reload, send
from ..library.whisper import permission
from bot import globals

@permission('owner')
def commandReload(args):
    reload.botReload(send.whisper(args.nick))
    return True

@permission('owner')
def commandReloadCommands(args):
    reload.botReloadCommands(send.whisper(args.nick))
    return True

@permission('owner')
def commandReloadConfig(args):
    reload.botReloadConfig(send.whisper(args.nick))
    return True
