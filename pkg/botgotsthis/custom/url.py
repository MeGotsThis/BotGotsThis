import re

import aiohttp

import bot
import lists.custom

from contextlib import suppress
from typing import Iterator, Match, List, Optional  # noqa: F401

from lib.data import CustomCommandField, CustomFieldArgs  # noqa: F401


async def fieldUrl(args: CustomFieldArgs) -> Optional[str]:
    if args.field.lower() == 'url':
        url: str = args.param
        match: Match[str]
        matches: List[Match[str]] = list(re.finditer(r'{([^\r\n\t\f {}]+)}',
                                                     args.param))
        for match in reversed(matches):
            s: int
            e: int
            s, e = match.span()
            url = url[:s] + await field_replace(args, match) + url[e:]
        urlTimeout: float = bot.config.customMessageUrlTimeout
        session: aiohttp.ClientSession
        response: aiohttp.ClientResponse
        with suppress(aiohttp.ClientError):
            async with aiohttp.ClientSession(
                    raise_for_status=True) as session,\
                    session.get(url, timeout=urlTimeout) as response:
                if response.status == 200:
                    data: str = await response.text()
                    data = data.replace('\r\n', ' ')
                    data = data.replace('\n', ' ')
                    data = data.replace('\r', ' ')
                    return (args.prefix or '') + data + (args.suffix or '')
        return args.default or ''
    return None


async def field_replace(args: CustomFieldArgs, match: Match[str]) -> str:
    newargs: CustomFieldArgs
    newargs = args._replace(field=match.group(1),
                            param=None,
                            prefix=None,
                            suffix=None,
                            default=None,
                            )
    fields: Iterator[CustomCommandField]
    fields = (f for f in lists.custom.fields() if f is not fieldUrl)
    field: CustomCommandField
    for field in fields:
        replacement: Optional[str] = await field(newargs)
        if replacement is not None:
            return replacement
    return ''
