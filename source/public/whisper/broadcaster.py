from ..library import broadcaster
from ..library.whisper import send
from ...data import WhisperCommandArgs


async def commandCome(args: WhisperCommandArgs) -> bool:
    return await broadcaster.come(args.database, args.nick, send(args.nick))


async def commandLeave(args: WhisperCommandArgs) -> bool:
    return broadcaster.leave(args.nick, send(args.nick))


async def commandEmpty(args: WhisperCommandArgs) -> bool:
    return broadcaster.empty(args.nick, send(args.nick))


async def commandAutoJoin(args: WhisperCommandArgs) -> bool:
    return await broadcaster.auto_join(args.database, args.nick,
                                       send(args.nick), args.message)

