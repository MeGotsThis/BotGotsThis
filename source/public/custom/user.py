from typing import Optional
from ...data import CustomFieldArgs


def fieldUser(args: CustomFieldArgs) -> Optional[str]:
    if args.field.lower() == 'user' or args.field.lower() == 'nick':
        if args.nick:
            return (args.prefix or '') + args.nick + (args.suffix or '')
        else:
            return args.default or ''
    return None
