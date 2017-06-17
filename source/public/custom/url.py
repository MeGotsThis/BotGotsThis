import re
import urllib.error
import urllib.request

import aiohttp

import bot.config
import lists.custom

from contextlib import suppress
from functools import partial
from http.client import HTTPResponse
from typing import BinaryIO, Callable, Iterator, Match, Optional, Union

from ...data import CustomCommandField, CustomFieldArgs


async def fieldUrl(args: CustomFieldArgs) -> Optional[str]:
    if args.field.lower() == 'url':
        replace_func: Callable[[Match[str]], str]
        replace_func = partial(field_replace, args)  # type: ignore
        url: str = re.sub(r'{([^\r\n\t\f {}]+)}', replace_func, args.param)
        urlTimeout: float = bot.config.customMessageUrlTimeout
        session: aiohttp.ClientSession
        response: aiohttp.ClientResponse
        with suppress(aiohttp.ClientError):
            async with aiohttp.ClientSession(raise_for_status=True) as session,\
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
    fields = (f for f in lists.custom.fields if f is not fieldUrl)
    field: CustomCommandField
    for field in fields:
        replacement: Optional[str] = await field(newargs)
        if replacement is not None:
            return replacement
    return ''
