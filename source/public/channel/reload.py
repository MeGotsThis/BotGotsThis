from ..library import reload
from ..library.chat import permission, ownerChannel, sendPriority
from ...data import ChatCommandArgs


@ownerChannel
@permission('owner')
def commandReload(args: ChatCommandArgs) -> bool:
    return reload.full_reload(sendPriority(args.chat, 0))


@ownerChannel
@permission('manager')
def commandReloadCommands(args: ChatCommandArgs) -> bool:
    return reload.reload_commands(sendPriority(args.chat, 0))


@ownerChannel
@permission('owner')
def commandReloadConfig(args: ChatCommandArgs) -> bool:
    return reload.reload_config(sendPriority(args.chat, 0))
