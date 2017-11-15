from typing import Optional

from lib.data import ChatCommandArgs
from lib.helper.chat import permission, ownerChannel, sendPriority
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


@ownerChannel
@permission('owner')
async def commandRefreshCache(args: ChatCommandArgs) -> bool:
    keys: Optional[str] = args.message[1] if len(args.message) >= 2 else None
    return await reload.refresh_cache(sendPriority(args.chat, 0), args.data,
                                      keys)
