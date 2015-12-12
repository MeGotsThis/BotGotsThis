from bot import config
import urllib.request

def fieldUrl(field, param, prefix, suffix, default, message,
             msgParts, channel, nick, query, now):
    if field.lower() == 'url':
        url = param.replace('{query}', query)
        url = url.replace('{user}', nick)
        url = url.replace('{nick}', nick)
        url = url.replace('{broadcaster}', channel)
        url = url.replace('{streamer}', channel)
        try:
            urlopen = urllib.request.urlopen
            req = urlopen(url, timeout=config.customMessageUrlTimeout)
            if int(req.status) == 200:
                data = req.read().decode('utf-8')
                data = data.replace('\r\n', ' ')
                data = data.replace('\n', ' ')
                data = data.replace('\r', ' ')
                return prefix + data + suffix
        except:
            pass
        return default
    return None
