﻿from bot import config
from contextlib import suppress
import urllib.error
import urllib.request

def fieldUrl(args):
    if args.field.lower() == 'url':
        url = args.param.replace('{query}', args.message.query)
        url = url.replace('{user}', args.nick)
        url = url.replace('{nick}', args.nick)
        url = url.replace('{broadcaster}', args.channel)
        url = url.replace('{streamer}', args.channel)
        with suppress(urllib.error.URLError):
            req = urllib.request.urlopen(
                url, timeout=config.customMessageUrlTimeout)
            if int(req.status) == 200:
                data = req.read().decode('utf-8')
                data = data.replace('\r\n', ' ')
                data = data.replace('\n', ' ')
                data = data.replace('\r', ' ')
                return args.prefix + data + args.suffix
        return args.default
    return None
