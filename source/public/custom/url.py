from contextlib import suppress
from functools import partial
from http.client import HTTPResponse
from typing import BinaryIO, Callable, Iterator, Match, Optional, Union
from ...data import CustomCommandField, CustomFieldArgs
import re
import bot.config
import lists.custom
import urllib.error
import urllib.request


def fieldUrl(args: CustomFieldArgs) -> Optional[str]:
    if args.field.lower() == 'url':
        replace_func: Callable[[Match[str]], str]
        replace_func = partial(field_replace, args)  # type: ignore
        url: str = re.sub(r'{([^\r\n\t\f {}]+)}', replace_func, args.param)
        with suppress(urllib.error.URLError):
            urlTimeout: float = bot.config.customMessageUrlTimeout
            res: Union[HTTPResponse, BinaryIO]
            with urllib.request.urlopen(url, timeout=urlTimeout) as res:
                if isinstance(res, HTTPResponse) and int(res.status) == 200:
                    data: str = res.read().decode('utf-8')
                    data = data.replace('\r\n', ' ')
                    data = data.replace('\n', ' ')
                    data = data.replace('\r', ' ')
                    return (args.prefix or '') + data + (args.suffix or '')
        return args.default or ''
    return None


def field_replace(args: CustomFieldArgs, match: Match[str]) -> str:
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
        replacement: Optional[str] = field(newargs)
        if replacement is not None:
            return replacement
    return ''
