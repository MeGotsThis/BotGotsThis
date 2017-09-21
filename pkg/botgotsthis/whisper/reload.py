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
