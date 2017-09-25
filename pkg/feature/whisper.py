from lib.data import WhisperCommandArgs
from lib.helper.whisper import min_args, send
from . import library


@min_args(2)
async def commandFeature(args: WhisperCommandArgs) -> bool:
    return await library.feature(args.database, args.nick, args.message,
                                 send(args.nick))
