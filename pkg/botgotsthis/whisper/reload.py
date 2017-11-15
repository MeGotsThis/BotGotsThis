from typing import Optional

from lib.data import WhisperCommandArgs
from lib.helper.whisper import permission, send
from ..library import reload


@permission('owner')
async def commandReload(args: WhisperCommandArgs) -> bool:
    return await reload.full_reload(send(args.nick))


@permission('manager')
async def commandReloadCommands(args: WhisperCommandArgs) -> bool:
    return await reload.reload_commands(send(args.nick))


@permission('owner')
async def commandReloadConfig(args: WhisperCommandArgs) -> bool:
    return await reload.reload_config(send(args.nick))


@permission('owner')
async def commandRefreshCache(args: WhisperCommandArgs) -> bool:
    keys: Optional[str] = args.message[1] if len(args.message) >= 2 else None
    return await reload.refresh_cache(send(args.nick), args.data, keys)
