import asyncio
import bot
import bot._config
import re
import sys
import importlib
from typing import Iterator, List, Match, Optional, Tuple  # noqa: F401
from lib.data import Send, timezones

_reload_lock: asyncio.Lock = asyncio.Lock()


def reloadable(module: str) -> bool:
    include = (module.startswith('lib') or module.startswith('pkg'))
    match: Optional[Match[str]]
    match = re.fullmatch(r'pkg\.([^\.]+)\.autoload(?:\..+)?', module)
    exclude = (
        module == 'pkg.botgotsthis.library.reload'
        or (match is not None and match.group(1) in bot.globals.pkgs))
    return include and not exclude


def is_submodule(module: str,
                 source: str) -> bool:
    return module == source or module.startswith(source + '.')


def key(module: str) -> Tuple[int, int, bool, str]:
    if is_submodule(module, 'lib.irccommand'):
        return 95, 0, module == 'lib.irccommand', module
    if module == 'lib.channel':
        return 96, 0, module == 'lib.channel', module
    if module == 'lib.whisper':
        return 97, 0, module == 'lib.whisper', module
    if module == 'lib.ircmessage':
        return 98, 0, module == 'lib.ircmessage', module

    if is_submodule(module, 'lib.data'):
        return 0, 0, module == 'lib.data', module
    if is_submodule(module, 'lib.database'):
        return 5, 0, module == 'lib.database', module

    if is_submodule(module, 'lib.api'):
        return 10, 0, module == 'lib.api', module

    match: Optional[Match[str]] = re.fullmatch(r'pkg\.(.+)', module)
    if match is not None:
        subparts: List[str] = match.group(1).split('.')
        for i in range(1, len(subparts) + 1):
            pkg: str = '.'.join(subparts[:i])
            if pkg in bot.globals.pkgs:
                index: int = bot.globals.pkgs.index(pkg)
                if is_submodule(module, f'pkg.{pkg}.library'):
                    return 41, index, module == f'pkg.{pkg}.library', module
                if is_submodule(module, f'pkg.{pkg}.tasks'):
                    return 43, index, module == f'pkg.{pkg}.tasks', module
                if is_submodule(module, f'pkg.{pkg}.manage'):
                    return 44, index, module == f'pkg.{pkg}.manage', module
                if is_submodule(module, f'pkg.{pkg}.custom'):
                    return 45, index, module == f'pkg.{pkg}.custom', module
                if is_submodule(module, f'pkg.{pkg}.channel'):
                    return 46, index, module == f'pkg.{pkg}.channel', module
                if is_submodule(module, f'pkg.{pkg}.whisper'):
                    return 47, index, module == f'pkg.{pkg}.whisper', module
                if is_submodule(module, f'pkg.{pkg}.items'):
                    return 56, index, module == f'pkg.{pkg}.items', module
                if module == f'pkg.{pkg}.ircmessage':
                    return 57, index, module == f'pkg.{pkg}.ircmessage', module
                if module == f'pkg.{pkg}':
                    return 58, index, module == f'pkg.{pkg}', module
                if is_submodule(module, f'pkg.{pkg}'):
                    return 42, index, module == f'pkg.{pkg}', module
                break
        return 40, -len(subparts), False, module
    if module == 'pkg':
        return 59, 0, module == 'pkg', module

    if is_submodule(module, 'lib.items'):
        return 89, 0, module == 'lib.items', module

    if module == 'lib':
        return 99, 0, module == 'lib', module
    if is_submodule(module, 'lib'):
        return 30, 0, module == 'lib', module
    return 20, -module.count('.'), False, module


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
