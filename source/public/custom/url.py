from contextlib import suppress
from functools import partial
from http.client import HTTPResponse
from typing import Callable, Iterator, Match, Optional
from ...data import CustomCommandField, CustomFieldArgs
import re
import bot.config
import lists.custom
import urllib.error
import urllib.request


def fieldUrl(args: CustomFieldArgs) -> Optional[str]:
    if args.field.lower() == 'url':
        replace_func = None  # type: Callable[[Match[str]], str]
        replace_func = partial(field_replace, args)  # type: ignore
        url = re.sub(r'{([^\r\n\t\f {}]+)}', replace_func, args.param)  # type: str
        with suppress(urllib.error.URLError):
            with urllib.request.urlopen(
                    url, timeout=bot.config.customMessageUrlTimeout) as res:  # type: HTTPResponse
                if isinstance(res, HTTPResponse) and int(res.status) == 200:
                    data = res.read().decode('utf-8')  # type: str
                    data = data.replace('\r\n', ' ')
                    data = data.replace('\n', ' ')
                    data = data.replace('\r', ' ')
                    return (args.prefix or '') + data + (args.suffix or '')
        return args.default or ''
    return None


def field_replace(args: CustomFieldArgs, match: Match[str]) -> str:
    newargs = args._replace(field=match.group(1),  # type: ignore
                            param=None,
                            prefix=None,
                            suffix=None,
                            default=None,
                            )  # type: CustomFieldArgs
    fields = (f for f in lists.custom.fields if f is not fieldUrl)  # type: Iterator[CustomCommandField]
    for field in fields:  # type: CustomCommandField
        replacement = field(newargs)  # type: Optional[str]
        if replacement is not None:
            return replacement
    return ''
