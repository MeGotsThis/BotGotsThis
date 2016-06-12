from typing import Optional
from ...data import CustomFieldArgs


def fieldUser(args: CustomFieldArgs) -> Optional[str]:
    if args.field.lower() == 'user' or args.field.lower() == 'args.nick':
        if args.nick:
            return args.prefix + args.nick + args.suffix
        else:
            return args.default
    return None
