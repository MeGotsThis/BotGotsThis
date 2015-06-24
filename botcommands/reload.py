import sys
import imp

def loadThisModule(module):
    _ = module.startswith('botcommands')
    _ = _ or module.startswith('botprivate')
    _ = _ or module.startswith('ircchannel')
    _ = _ or module.startswith('ircwhisper')
    _ = _ or module.startswith('privatechannel')
    _ = _ or module.startswith('privatewhisper')
    _ = _ or module.startswith('database')
    return  _ and module != 'botcommands.reload'

def moduleKey(module):
    if module == 'database.databasebase':
        return (9, module)
    if module == 'database.factory':
        return (8, module)
    if module == 'database':
        return (0, module)
    if module.startswith('database'):
        return (1, module)

    if module.startswith('botprivate'):
        return (600, module)
    
    if module.startswith('botcommands'):
        return (700, module)
    
    if module == 'privatewhisper.commandList':
        return (889, module)
    if module == 'privatewhisper':
        return (880, module)
    if module.startswith('privatewhisper'):
        return (881, module)
    
    if module == 'privatechannel.commandList':
        return (899, module)
    if module == 'privatechannel':
        return (890, module)
    if module.startswith('privatechannel'):
        return (891, module)
    
    if module == 'ircwhisper.commandList':
        return (989, module)
    if module == 'ircwhisper':
        return (980, module)
    if module.startswith('ircwhisper'):
        return (981, module)
    
    if module == 'ircchannel.commandList':
        return (999, module)
    if module == 'ircchannel':
        return (990, module)
    if module.startswith('ircchannel'):
        return (991, module)
    
    return (100, module)

def botReload(sendMessage, nick, message, msgParts, permissions):
    sendMessage('Reloading', 0)
    
    botReloadCommands(sendMessage, nick, message, msgParts, permissions)
    botReloadConfig(sendMessage, nick, message, msgParts, permissions)
    
    sendMessage('Complete', 0)
    return True

def botReloadCommands(sendMessage, nick, message, msgParts, permissions):
    sendMessage('Reloading Commands', 0)
    
    modules = [m for m in sys.modules.keys() if loadThisModule(m)]
    for moduleString in sorted(modules, key=moduleKey):
        imp.reload(sys.modules[moduleString])
    
    sendMessage('Complete Reloading', 0)
    return True

def botReloadConfig(sendMessage, nick, message, msgParts, permissions):
    sendMessage('Reloading Config', 0)
    
    imp.reload(sys.modules['config.config'])
    
    sendMessage('Complete Reloading', 0)
    return True
