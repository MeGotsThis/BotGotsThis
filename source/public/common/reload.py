import sys
import imp

def loadThisModule(module):
    include = module.startswith('source') or module.startswith('lists')
    exclude = module == 'source.public.common.reload'
    exclude = exclude or module.startswith('source.private.autoload')
    exclude = exclude or module.startswith('source.public.autoload')
    return include and not exclude

def moduleKey(module):
    if module == 'source.database':
        return (0, module)
    if module == 'source.database.databasebase':
        return (1, module)
    if module == 'source.database.factory':
        return (9, module)
    if module.startswith('source.database'):
        return (8, module)

    if module.startswith('source.api'):
        return (10, module)
    if module.startswith('source.data'):
        return (11, module)
    if module.startswith('source.public.common'):
        return (18, module)
    if module.startswith('source.private.common'):
        return (19, module)
    
    if module.startswith('source.public.tasks'):
        return (20, module)
    if module.startswith('source.private.tasks'):
        return (21, module)
    
    if module.startswith('source.public.manage'):
        return (60, module)
    if module.startswith('source.private.manage'):
        return (61, module)
    if module.startswith('source.public.custom'):
        return (60, module)
    if module.startswith('source.private.custom'):
        return (61, module)
    
    if module.startswith('source.public.channel'):
        return (70, module)
    if module.startswith('source.private.channel'):
        return (71, module)
    if module.startswith('source.public.whisper'):
        return (72, module)
    if module.startswith('source.private.whisper'):
        return (73, module)
    
    if module.startswith('lists.private'):
        return (87, module)
    if module.startswith('lists.public'):
        return (88, module)
    if module.startswith('lists'):
        return (89, module)
    
    if module.startswith('source.irccommand'):
        return (96, module)
    if module == 'source.channel':
        return (97, module)
    if module == 'source.whisper':
        return (98, module)
    if module == 'source.ircmessage':
        return (99, module)
    
    return (50, module)

def botReload(send, nick, message, msgParts, permissions):
    send('Reloading', 0)
    
    botReloadCommands(send, nick, message, msgParts, permissions)
    botReloadConfig(send, nick, message, msgParts, permissions)
    
    send('Complete', 0)
    return True

def botReloadCommands(send, nick, message, msgParts, permissions):
    send('Reloading Commands', 0)
    
    modules = [m for m in sys.modules.keys() if loadThisModule(m)]
    for moduleString in sorted(modules, key=moduleKey):
        imp.reload(sys.modules[moduleString])
    
    send('Complete Reloading', 0)
    return True

def botReloadConfig(send, nick, message, msgParts, permissions):
    send('Reloading Config', 0)
    
    imp.reload(sys.modules['bot.config'])
    
    send('Complete Reloading', 0)
    return True
