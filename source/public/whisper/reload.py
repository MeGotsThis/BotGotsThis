from ..library import reload
from ..library.whisper import permission, send
from ...data.argument import WhisperCommandArgs


@permission('owner')
def commandReload(args: WhisperCommandArgs) -> bool:
    reload.botReload(send(args.nick))
    return True


@permission('owner')
def commandReloadCommands(args: WhisperCommandArgs) -> bool:
    reload.botReloadCommands(send(args.nick))
    return True


@permission('owner')
def commandReloadConfig(args: WhisperCommandArgs) -> bool:
    reload.botReloadConfig(send(args.nick))
    return True
