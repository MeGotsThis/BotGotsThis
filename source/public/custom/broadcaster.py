from typing import Optional
from ...data import CustomFieldArgs


def fieldBroadcaster(args: CustomFieldArgs) -> Optional[str]:
    if args.field.lower() in ['broadcaster', 'streamer']:
        if args.channel:
            return (args.prefix or '') + args.channel + (args.suffix or '')
        else:
            return args.default or ''
    return None
