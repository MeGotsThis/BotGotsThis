﻿from lib.data import WhisperCommandArgs
from lib.helper.whisper import min_args, send
from ..library import feature


@min_args(2)
async def commandFeature(args: WhisperCommandArgs) -> bool:
    return await feature.feature(args.database, args.nick, args.message,
                                 send(args.nick))
