from ..library import broadcaster
from ..library.whisper import send
from bot import globals

def commandCome(args):
    broadcaster.botCome(args.database, args.nick, send(args.nick))
    return True

def commandLeave(args):
    return broadcaster.botLeave(args.nick, send(args.nick))

def commandEmpty(args):
    broadcaster.botEmpty(args.nick, send(args.nick))
    return True

def commandAutoJoin(args):
    broadcaster.botAutoJoin(args.database, args.nick, send(args.nick),
                            args.message)
    return True

