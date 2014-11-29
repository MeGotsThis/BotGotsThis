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
    if module == 'database.database':
        return (5, module)
    if module == 'database.factory':
        return (4, module)
    if module == 'database':
        return (3, module)
    if module.startswith('database'):
        return (6, module)
    
    if module.startswith('database'):
        return (3, module)
    
    if module.startswith('privatechannel'):
        return (2, module)
    
    if module.startswith('ircchannel'):
        return (1, module)
    
    return (0, module)

def commandReload(channelThread, nick, message, msgParts, permissions):
    channelThread.sendMessage('Reloading', 0)
    
    commandReloadAllMods(channelThread, nick, message, msgParts, permissions)
    commandReloadCommands(channelThread, nick, message, msgParts, permissions)
    commandReloadConfig(channelThread, nick, message, msgParts, permissions)
    
    channelThread.sendMessage('Complete', 0)
    return True

def commandReloadCommands(channelThread, nick, message, msgParts, permissions):
    channelThread.sendMessage('Reloading Commands', 0)
    
    modules = [m for m in sys.modules.keys() if loadThisModule(m)]
    for moduleString in sorted(modules, key=moduleKey, reverse=True):
        imp.reload(sys.modules[moduleString])
    
    channelThread.sendMessage('Complete Commands', 0)
    return True

def commandReloadConfig(channelThread, nick, message, msgParts, permissions):
    channelThread.sendMessage('Reloading Config', 0)
    
    imp.reload(sys.modules['config.config'])
    
    channelThread.sendMessage('Complete Config', 0)
    return True

def commandReloadAllMods(channelThread, nick, message, msgParts, permissions):
    channelThread.sendMessage('Reloading Mods', 0)
    for channel in set(ircbot.irc.channels.keys()):
        ircbot.irc.channels[channel].mods.clear()
        ircbot.irc.channels[channel].sendMessage('.mods', 0)
    channelThread.sendMessage('Complete Mods', 0)
    return True
