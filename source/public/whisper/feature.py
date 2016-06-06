from ..library import feature
from ..library.whisper import send


def commandFeature(args):
    return feature.botFeature(args.database, args.nick, args.message,
                              send(args.nick))
