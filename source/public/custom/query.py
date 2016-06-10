from typing import Optional
from ...data.argument import CustomFieldArgs


def fieldQuery(args: CustomFieldArgs) -> Optional[str]:
    if args.field.lower() == 'query':
        if len(args.message) > 1:
            return args.prefix + args.message.query + args.suffix
        else:
            return args.default
    return None
