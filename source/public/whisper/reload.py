from ..library import reload
from ..library.whisper import permission, send
from ...data import WhisperCommandArgs


@permission('owner')
async def commandReload(args: WhisperCommandArgs) -> bool:
    return await reload.full_reload(send(args.nick))


@permission('manager')
async def commandReloadCommands(args: WhisperCommandArgs) -> bool:
    return reload.reload_commands(send(args.nick))


@permission('owner')
async def commandReloadConfig(args: WhisperCommandArgs) -> bool:
    return await reload.reload_config(send(args.nick))
