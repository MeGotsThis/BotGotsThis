from ..library import feature
from ..library.whisper import min_args, send
from ...data import WhisperCommandArgs


@min_args(2)
async def commandFeature(args: WhisperCommandArgs) -> bool:
    return await feature.feature(args.database, args.nick, args.message,
                                 send(args.nick))
