import asyncio
import bot
import sys
import importlib
from typing import Iterator, Tuple  # noqa: F401
from ...data import Send, timezones

_reload_lock: asyncio.Lock = asyncio.Lock()


def reloadable(module: str) -> bool:
    include = module.startswith('source') or module.startswith('lists')
    exclude = module in ['source.public.library.reload',
                         'source.private.autoload',
                         'source.public.autoload']
    exclude = exclude or module.startswith('source.private.autoload.')
    exclude = exclude or module.startswith('source.public.autoload.')
    return include and not exclude


def is_submodule(module: str,
                 source: str) -> bool:
    return module == source or module.startswith(source + '.')


def key(module: str) -> Tuple[int, str]:
    if module == 'source.private.ircmessage':
        return 90, module
    if module == 'source.public.default.ircmessage':
        return 91, module
    if module.startswith('source.irccommand.'):
        return 92, module
    if module == 'source.irccommand':
        return 93, module
    if module == 'source.channel':
        return 97, module
    if module == 'source.whisper':
        return 98, module
    if module == 'source.ircmessage':
        return 99, module

    if is_submodule(module, 'source.data'):
        return 0, module
    if module == 'source.database':
        return 1, module
    if module.startswith('source.database.'):
        return 9, module

    if is_submodule(module, 'source.api'):
        return 10, module
    if is_submodule(module, 'source.public.library'):
        return 18, module
    if is_submodule(module, 'source.private.library'):
        return 19, module

    if is_submodule(module, 'source.public.tasks'):
        return 20, module
    if is_submodule(module, 'source.private.tasks'):
        return 21, module

    if is_submodule(module, 'source.public.manage'):
        return 60, module
    if is_submodule(module, 'source.private.manage'):
        return 61, module
    if is_submodule(module, 'source.public.custom'):
        return 62, module
    if is_submodule(module, 'source.private.custom'):
        return 63, module

    if is_submodule(module, 'source.public.channel'):
        return 70, module
    if is_submodule(module, 'source.private.channel'):
        return 71, module
    if is_submodule(module, 'source.public.whisper'):
        return 72, module
    if is_submodule(module, 'source.private.whisper'):
        return 73, module

    if module.startswith('lists.private.'):
        return 84, module
    if module == 'lists.private':
        return 85, module
    if module.startswith('lists.public.'):
        return 86, module
    if module == 'lists.public':
        return 87, module
    if module.startswith('lists.'):
        return 88, module
    if module == 'lists':
        return 89, module

    if is_submodule(module, 'source.public'):
        return 58, module
    if is_submodule(module, 'source.private'):
        return 59, module
    if is_submodule(module, 'source.'):
        return 51, module
    return 50, module


async def full_reload(send: Send) -> bool:
    if _reload_lock.locked():
        return True

    with await _reload_lock:
        send('Reloading')

        await reload_config(send)
        await reload_commands(send)

        send('Complete')
        return True


async def reload_commands(send: Send) -> bool:
    if _reload_lock.locked():
        return True

    with await _reload_lock:
        send('Reloading Commands')

        modules: Iterator[str]
        modules = (m for m in sys.modules.keys() if reloadable(m))
        moduleString: str
        for moduleString in sorted(modules, key=key):
            importlib.reload(sys.modules[moduleString])
        await timezones.load_timezones()

        send('Complete Reloading')
        return True


async def reload_config(send: Send) -> bool:
    if _reload_lock.locked():
        return True

    with await _reload_lock:
        send('Reloading Config')

        importlib.reload(sys.modules['bot'])
        config: bot.BotConfig = bot.BotConfig()
        await config.read_config()
        bot.config = config

        send('Complete Reloading')
        return True
