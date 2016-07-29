from contextlib import suppress
from typing import Match, Optional, Sequence
from ...data import CustomFieldArgs
import re


def fieldParams(args: CustomFieldArgs) -> Optional[str]:
    with suppress(TypeError):
        match = re.fullmatch(r'(\d+)(-(\d+))?|(\d+)-|-(\d+)', args.field)  # type: Match[str]
        if match is not None:
            prefix = args.prefix or ''
            suffix = args.suffix or ''
            matchParts = match.groups()  # type: Sequence[str]
            start = None  # type: Optional[int]
            stop = None  # type: Optional[int]
            if matchParts[0] is not None:
                start = int(matchParts[0])
                if matchParts[2] is not None:
                    stop = int(matchParts[2]) + 1
                else:
                    if start < len(args.message):
                        return prefix + args.message[start] + suffix
                    else:
                        return args.default or ''
            elif matchParts[3] is not None:
                start = int(matchParts[3])
            elif matchParts[4] is not None:
                start = 1
                stop = int(matchParts[4]) + 1
            params = args.message[start:stop]
            if params:
                return prefix + params + suffix
            else:
                return args.default or ''
    return None
