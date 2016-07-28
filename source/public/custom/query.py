from typing import Optional
from ...data import CustomFieldArgs


def fieldQuery(args: CustomFieldArgs) -> Optional[str]:
    if args.field.lower() == 'query':
        if len(args.message) > 1:
            prefix = args.prefix or ''  # type: str
            suffix = args.suffix or ''  # type: str
            return prefix + args.message.query + suffix
        else:
            return args.default or ''
    return None
