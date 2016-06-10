import sys
import importlib
from typing import Tuple
from ...data.argument import Send
from ...data.message import Message


def loadThisModule(module: str) -> bool:
    include = module.startswith('source') or module.startswith('lists')
    exclude = module == 'source.public.library.reload'
    exclude = exclude or module.startswith('source.private.autoload')
    exclude = exclude or module.startswith('source.public.autoload')
    return include and not exclude


def moduleKey(module: str) -> Tuple[int, str]:
    if module.startswith('source.irccommand'):
        return 90, module
    if module == 'source.public.channel.text':
        return 96, module
    if module == 'source.public.library.feature':
        return 96, module
    if module == 'source.public.library.managebot':
        return 96, module
    if module == 'source.channel':
        return 97, module
    if module == 'source.whisper':
        return 98, module
    if module == 'source.ircmessage':
        return 99, module
    
    if module.startswith('source.data'):
        return 0, module
    if module == 'source.database':
        return 1, module
    if module == 'source.database.databasebase':
        return 2, module
    if module == 'source.database.factory':
        return 9, module
    if module.startswith('source.database'):
        return 8, module

    if module.startswith('source.api'):
        return 10, module
    if module.startswith('source.public.library'):
        return 18, module
    if module.startswith('source.private.library'):
        return 19, module
    
    if module.startswith('source.public.tasks'):
        return 20, module
    if module.startswith('source.private.tasks'):
        return 21, module
    
    if module.startswith('source.public.manage'):
        return 60, module
    if module.startswith('source.private.manage'):
        return 61, module
    if module.startswith('source.public.custom'):
        return 60, module
    if module.startswith('source.private.custom'):
        return 61, module
    
    if module.startswith('source.public.channel'):
        return 70, module
    if module.startswith('source.private.channel'):
        return 71, module
    if module.startswith('source.public.whisper'):
        return 72, module
    if module.startswith('source.private.whisper'):
        return 73, module
    
    if module.startswith('lists.private'):
        return 87, module
    if module.startswith('lists.public'):
        return 88, module
    if module.startswith('lists'):
        return 89, module
    
    return 50, module


def botReload(send: Send):
    send('Reloading')
    
    botReloadCommands(send)
    botReloadConfig(send)
    
    send('Complete')
    return True


def botReloadCommands(send: Send):
    send('Reloading Commands')
    
    modules = [m for m in sys.modules.keys() if loadThisModule(m)]  # type: List[str]
    for moduleString in sorted(modules, key=moduleKey):  # --type: str
        importlib.reload(sys.modules[moduleString])
    
    send('Complete Reloading')
    return True


def botReloadConfig(send: Send):
    send('Reloading Config')
    
    importlib.reload(sys.modules['bot.config'])
    
    send('Complete Reloading')
    return True
