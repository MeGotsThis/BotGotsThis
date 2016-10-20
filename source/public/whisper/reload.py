from ..library import reload
from ..library.whisper import permission, send
from ...data import WhisperCommandArgs


@permission('owner')
def commandReload(args: WhisperCommandArgs) -> bool:
    return reload.full_reload(send(args.nick))


@permission('manager')
def commandReloadCommands(args: WhisperCommandArgs) -> bool:
    return reload.reload_commands(send(args.nick))


@permission('owner')
def commandReloadConfig(args: WhisperCommandArgs) -> bool:
    return reload.reload_config(send(args.nick))
