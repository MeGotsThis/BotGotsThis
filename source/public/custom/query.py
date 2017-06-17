from typing import Optional
from ...data import CustomFieldArgs


async def fieldQuery(args: CustomFieldArgs) -> Optional[str]:
    if args.field.lower() == 'query':
        if len(args.message) > 1:
            prefix: str = args.prefix or ''
            suffix: str = args.suffix or ''
            return prefix + args.message.query + suffix
        else:
            return args.default or ''
    return None
