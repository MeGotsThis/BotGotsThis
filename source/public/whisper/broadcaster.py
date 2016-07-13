from ..library import broadcaster
from ..library.whisper import send
from ...data import WhisperCommandArgs


def commandCome(args: WhisperCommandArgs) -> bool:
    return broadcaster.come(args.database, args.nick, send(args.nick))


def commandLeave(args: WhisperCommandArgs) -> bool:
    return broadcaster.leave(args.nick, send(args.nick))


def commandEmpty(args: WhisperCommandArgs) -> bool:
    return broadcaster.empty(args.nick, send(args.nick))


def commandAutoJoin(args: WhisperCommandArgs) -> bool:
    return broadcaster.auto_join(args.database, args.nick, send(args.nick),
                                 args.message)

