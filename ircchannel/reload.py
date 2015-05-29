from config import config
import ircbot.irc
import time
import sys
import imp

def loadThisModule(module):
    _ = module.startswith('ircchannel')
    _ = _ or module.startswith('privatechannel')
    _ = _ or module.startswith('database')
    return  _ and module != 'ircchannel.reload'

def moduleKey(module):
    if module == 'database.databasebase':
        return (9, module)
    if module == 'database.factory':
        return (8, module)
    if module == 'database':
        return (0, module)
    if module.startswith('database'):
        return (1, module)
    
    if module == 'privatechannel.commandList':
        return (989, module)
    if module == 'privatechannel':
        return (980, module)
    if module.startswith('privatechannel'):
        return (981, module)
    
    if module == 'ircchannel.commandList':
        return (999, module)
    if module == 'ircchannel':
        return (990, module)
    if module.startswith('ircchannel'):
        return (991, module)
    
    return (100, module)

def commandReload(channelData, nick, message, msgParts, permissions):
    channelData.sendMessage('Reloading', 0)
    
    commandReloadCommands(channelData, nick, message, msgParts, permissions)
    commandReloadConfig(channelData, nick, message, msgParts, permissions)
    
    channelData.sendMessage('Complete', 0)
    return True

def commandReloadCommands(channelData, nick, message, msgParts, permissions):
    channelData.sendMessage('Reloading Commands', 0)
    
    modules = [m for m in sys.modules.keys() if loadThisModule(m)]
    for moduleString in sorted(modules, key=moduleKey):
        imp.reload(sys.modules[moduleString])
    
    channelData.sendMessage('Complete Commands', 0)
    return True

def commandReloadConfig(channelData, nick, message, msgParts, permissions):
    channelData.sendMessage('Reloading Config', 0)
    
    imp.reload(sys.modules['config.config'])
    
    channelData.sendMessage('Complete Config', 0)
    return True
