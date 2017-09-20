from source.data import ChatCommandArgs
from source.helper.chat import permission, ownerChannel, sendPriority
from ..library import reload


@ownerChannel
@permission('owner')
async def commandReload(args: ChatCommandArgs) -> bool:
    return await reload.full_reload(sendPriority(args.chat, 0))


@ownerChannel
@permission('manager')
async def commandReloadCommands(args: ChatCommandArgs) -> bool:
    return await reload.reload_commands(sendPriority(args.chat, 0))


@ownerChannel
@permission('owner')
async def commandReloadConfig(args: ChatCommandArgs) -> bool:
    return await reload.reload_config(sendPriority(args.chat, 0))
