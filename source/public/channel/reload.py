from ..library import reload
from ..library.chat import permission, ownerChannel, sendPriority
from ...data.argument import ChatCommandArgs


@ownerChannel
@permission('owner')
def commandReload(args: ChatCommandArgs) -> bool:
    reload.botReload(sendPriority(args.chat, 0))
    return True


@ownerChannel
@permission('owner')
def commandReloadCommands(args: ChatCommandArgs) -> bool:
    reload.botReloadCommands(sendPriority(args.chat, 0))
    return True


@ownerChannel
@permission('owner')
def commandReloadConfig(args: ChatCommandArgs) -> bool:
    reload.botReloadConfig(sendPriority(args.chat, 0))
    return True
