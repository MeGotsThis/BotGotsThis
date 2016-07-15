﻿from ..library import feature
from ..library.chat import min_args, permission, send
from ...data import ChatCommandArgs


@permission('broadcaster')
@min_args(2)
def commandFeature(args: ChatCommandArgs) -> bool:
    return feature.feature(args.database, args.chat.channel, args.message,
                           send(args.chat))
