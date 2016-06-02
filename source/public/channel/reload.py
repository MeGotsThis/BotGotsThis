from ..library import reload, send
from ..library.chat import permission, ownerChannel

@ownerChannel
@permission('owner')
def commandReload(args):
    reload.botReload(send.channel(args.chat))
    return True

@ownerChannel
@permission('owner')
def commandReloadCommands(args):
    reload.botReloadCommands(send.channel(args.chat))
    return True

@ownerChannel
@permission('owner')
def commandReloadConfig(args):
    reload.botReloadConfig(send.channel(args.chat))
    return True
