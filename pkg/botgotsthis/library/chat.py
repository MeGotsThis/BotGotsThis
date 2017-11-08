import bot
from typing import Dict, Optional  # noqa: F401
from lib.cache import CacheStore
from lib.data import Send
from lib.data.message import Message


def empty(channel: str,
          send: Send) -> bool:
    if channel in bot.globals.channels:
        chan = bot.globals.channels[channel]
        chan.clear()
        send(f'Cleared all queued messages for {channel}')
    return True


async def set_timeout_level(data: CacheStore,
                            channel: str,
                            send: Send,
                            message: Message) -> bool:
    propertyDict: Dict[str, str] = {
        '1': 'timeoutLength0',
        '2': 'timeoutLength1',
        '3': 'timeoutLength2',
        }
    ordinal: Dict[str, str] = {
        '1': '1st',
        '2': '2nd',
        '3': '3rd',
        }
    k: str = message.command.split('settimeoutlevel-')[1]
    if k not in propertyDict:
        return False
    value: Optional[int]
    try:
        value = int(message[1])
    except (ValueError, IndexError):
        value = None
    timeout: int = bot.config.moderatorDefaultTimeout[int(k) - 1]
    default: str = f'{timeout} seconds' if timeout else 'Banned'
    saveValue: Optional[str] = str(value) if value is not None else None
    await data.setChatProperty(channel, propertyDict[k], saveValue)
    if value is None:
        send(f'''\
Setting the timeout length for {ordinal[k]} offense to defaulted amount \
({default})''')
    elif value:
        send(f'''\
Setting the timeout length for {ordinal[k]} offense to {value} seconds''')
    else:
        send(f'Setting the timeout length for {ordinal[k]} offense to banning')
    return True
