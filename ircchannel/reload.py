from config import config
import ircbot.irc
import time
import sys
import imp

def commandReload(channelThread, nick, message, msgParts, permissions):
    channelThread.sendMessage('Reloading', 0)
    
    commandReloadCommands(channelThread, nick, message, msgParts, permissions)
    commandReloadConfig(channelThread, nick, message, msgParts, permissions)
    
    channelThread.sendMessage('Complete', 0)
    return True

def commandReloadCommands(channelThread, nick, message, msgParts, permissions):
    channelThread.sendMessage('Reloading Commands', 0)
    
    modules = [m for m in sys.modules.keys()
               if m.startswith('ircchannel') and m != 'ircchannel.reload']
    for moduleString in modules:
        imp.reload(sys.modules[moduleString])
    
    channelThread.sendMessage('Complete Commands', 0)
    return True

def commandReloadConfig(channelThread, nick, message, msgParts, permissions):
    channelThread.sendMessage('Reloading Config', 0)
    
    imp.reload(sys.modules['config.config'])
    
    channelThread.sendMessage('Complete Config', 0)
    return True
