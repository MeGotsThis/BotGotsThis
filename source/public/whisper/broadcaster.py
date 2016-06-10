from ..library import broadcaster
from ..library.whisper import send
from ...data.argument import WhisperCommandArgs


def commandCome(args: WhisperCommandArgs) -> bool:
    broadcaster.botCome(args.database, args.nick, send(args.nick))
    return True


def commandLeave(args: WhisperCommandArgs) -> bool:
    return broadcaster.botLeave(args.nick, send(args.nick))


def commandEmpty(args: WhisperCommandArgs) -> bool:
    broadcaster.botEmpty(args.nick, send(args.nick))
    return True


def commandAutoJoin(args: WhisperCommandArgs) -> bool:
    broadcaster.botAutoJoin(args.database, args.nick, send(args.nick),
                            args.message)
    return True

