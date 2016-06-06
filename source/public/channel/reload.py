from ..library import reload
from ..library.chat import permission, ownerChannel, send


@ownerChannel
@permission('owner')
def commandReload(args):
    reload.botReload(send(args.chat))
    return True


@ownerChannel
@permission('owner')
def commandReloadCommands(args):
    reload.botReloadCommands(send(args.chat))
    return True


@ownerChannel
@permission('owner')
def commandReloadConfig(args):
    reload.botReloadConfig(send(args.chat))
    return True
