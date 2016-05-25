from ..library import broadcaster, send
from bot import globals

def commandCome(args):
    broadcaster.botCome(args.database, args.nick, send.whisper(args.nick))
    return True

def commandLeave(args):
    return broadcaster.botLeave(args.nick, send.whisper(args.nick))

def commandEmpty(args):
    broadcaster.botEmpty(args.nick, send.whisper(args.nick))
    return True

def commandAutoJoin(args):
    broadcaster.botAutoJoin(args.database, args.nick, send.whisper(args.nick),
                            args.message)
    return True

