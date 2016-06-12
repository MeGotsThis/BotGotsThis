from typing import Optional
from ...data import CustomFieldArgs


def fieldBroadcaster(args: CustomFieldArgs) -> Optional[str]:
    if args.field.lower() == 'broadcaster' or args.field.lower() == 'streamer':
        if args.channel:
            return args.prefix + args.channel + args.suffix
        else:
            return args.default
    return None
