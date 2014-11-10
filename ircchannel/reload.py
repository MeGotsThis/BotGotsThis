from config import config
import ircbot.irc
import time
import sys
import imp

def commandReload(channelThread, nick, message, msgParts, permissions):
    channelThread.sendMessage('Reloading', 0)
    
    modules = [m for m in sys.modules.keys()
               if m.startswith('ircchannel') and m != 'ircchannel.reload']
    for moduleString in modules:
        imp.reload(sys.modules[moduleString])
    
    channelThread.sendMessage('Complete', 0)
    return True
