from typing import Optional
from source.data import CustomFieldArgs


async def fieldBroadcaster(args: CustomFieldArgs) -> Optional[str]:
    if args.field.lower() in ['broadcaster', 'streamer']:
        if args.channel:
            return (args.prefix or '') + args.channel + (args.suffix or '')
        else:
            return args.default or ''
    return None
