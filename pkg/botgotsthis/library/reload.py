import asyncio
import bot
import bot._config
import re
import sys
import importlib
from typing import Iterator, Tuple  # noqa: F401
from source.data import Send, timezones

_reload_lock: asyncio.Lock = asyncio.Lock()


def reloadable(module: str) -> bool:
    include = (module.startswith('source') or module.startswith('lists')
               or module.startswith('pkg'))
    exclude = module in ['pkg.botgotsthis.library.reload',
                         'source.private.autoload',
                         'source.public.autoload']
    exclude = exclude or module.startswith('source.private.autoload.')
    exclude = exclude or re.fullmatch(r'pkg\.[^\.]+\.autoload(\..+)?', module)
    return include and not exclude


def is_submodule(module: str,
                 source: str) -> bool:
    return module == source or module.startswith(source + '.')


def key(module: str) -> Tuple[int, bool, str]:
    if is_submodule(module, 'source.irccommand'):
        return 95, module == 'source.irccommand', module
    if module == 'source.channel':
        return 96, module == 'source.channel', module
    if module == 'source.whisper':
        return 97, module == 'source.whisper', module
    if module == 'source.ircmessage':
        return 98, module == 'source.ircmessage', module

    if is_submodule(module, 'source.data'):
        return 0, module == 'source.data', module
    if is_submodule(module, 'source.database'):
        return 5, module == 'source.database', module

    if is_submodule(module, 'source.api'):
        return 10, module == 'source.api', module
    if is_submodule(module, 'source.private.library'):
        return 15, module == 'source.private.library', module

    if is_submodule(module, 'pkg.botgotsthis.library'):
        return 31, module == 'pkg.botgotsthis.library', module
    if is_submodule(module, 'pkg.botgotsthis.tasks'):
        return 35, module == 'pkg.botgotsthis.tasks', module
    if is_submodule(module, 'pkg.botgotsthis.manage'):
        return 36, module == 'pkg.botgotsthis.manage', module
    if is_submodule(module, 'pkg.botgotsthis.custom'):
        return 37, module == 'pkg.botgotsthis.custom', module
    if is_submodule(module, 'pkg.botgotsthis.channel'):
        return 38, module == 'pkg.botgotsthis.channel', module
    if is_submodule(module, 'pkg.botgotsthis.whisper'):
        return 39, module == 'pkg.botgotsthis.whisper', module
    if is_submodule(module, 'pkg.botgotsthis.items'):
        return 47, module == 'pkg.botgotsthis.items', module
    if module == 'pkg.botgotsthis.ircmessage':
        return 48, module == 'pkg.botgotsthis.ircmessage', module
    if module == 'pkg.botgotsthis':
        return 49, module == 'pkg.botgotsthis', module
    if is_submodule(module, 'pkg.botgotsthis'):
        return 30, module == 'pkg.botgotsthis', module

    if module.startswith('lists'):
        return 89, module == 'lists', module

    if module == 'source':
        return 99, module == 'source', module
    if is_submodule(module, 'source'):
        return 20, module == 'source', module
    return 20, False, module


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

        importlib.reload(sys.modules['bot._config'])
        config: bot._config.BotConfig = bot._config.BotConfig()
        await config.read_config()
        bot.config = config

        send('Complete Reloading')
        return True
