from ..library import reload
from ..library.chat import permission, ownerChannel, send
from ...data.argument import ChatCommandArgs


@ownerChannel
@permission('owner')
def commandReload(args: ChatCommandArgs) -> bool:
    reload.botReload(send(args.chat))
    return True


@ownerChannel
@permission('owner')
def commandReloadCommands(args: ChatCommandArgs) -> bool:
    reload.botReloadCommands(send(args.chat))
    return True


@ownerChannel
@permission('owner')
def commandReloadConfig(args: ChatCommandArgs) -> bool:
    reload.botReloadConfig(send(args.chat))
    return True
