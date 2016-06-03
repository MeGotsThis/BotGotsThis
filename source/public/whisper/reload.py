from ..library import reload
from ..library.whisper import permission, send
from bot import globals

@permission('owner')
def commandReload(args):
    reload.botReload(send(args.nick))
    return True

@permission('owner')
def commandReloadCommands(args):
    reload.botReloadCommands(send(args.nick))
    return True

@permission('owner')
def commandReloadConfig(args):
    reload.botReloadConfig(send(args.nick))
    return True
