from ..library import feature, send
from bot import globals

def commandFeature(args):
    return feature.botFeature(args.database, args.nick, args.message,
                              send.whisper(args.nick))
