from ..library import feature
from ..library.whisper import send
from ...data import WhisperCommandArgs


def commandFeature(args: WhisperCommandArgs) -> bool:
    return feature.botFeature(args.database, args.nick, args.message,
                              send(args.nick))
