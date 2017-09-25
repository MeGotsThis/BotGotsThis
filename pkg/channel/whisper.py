from lib.data import WhisperCommandArgs
from lib.helper.whisper import send
from . import library


async def commandCome(args: WhisperCommandArgs) -> bool:
    return await library.come(args.database, args.nick, send(args.nick))


async def commandLeave(args: WhisperCommandArgs) -> bool:
    return await library.leave(args.nick, send(args.nick))


async def commandAutoJoin(args: WhisperCommandArgs) -> bool:
    return await library.auto_join(args.database, args.nick, send(args.nick),
                                   args.message)
