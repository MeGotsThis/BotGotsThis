from ..library import feature
from ..library.whisper import send
from bot import globals

def commandFeature(args):
    return feature.botFeature(args.database, args.nick, args.message,
                              send(args.nick))
