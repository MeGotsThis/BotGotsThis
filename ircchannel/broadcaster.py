from config import config
import database.factory
import ircbot.twitchApi
import ircbot.irc
import threading
import time

def commandHello(channelData, nick, message, msgParts, permissions):
    channelData.sendMessage('Hello Kappa')
    return True

def commandCome(channelData, nick, message, msgParts, permissions):
    if ('#' + nick) in ircbot.irc.channels:
        channelData.sendMessage('I am already in ' + nick)
        return True
    channelData.sendMessage('Joining ' + nick)
    ircbot.irc.joinChannel(nick)
    return True

def commandLeave(channelData, nick, message, msgParts, permissions):
    if channelData.channel == '#' + config.botnick:
        return False
    channelData.sendMessage('Bye ' + channelData.channel[1:])
    time.sleep(1)
    ircbot.irc.partChannel(channelData.channel)
    return True

def commandEmpty(channelData, nick, message, msgParts, permissions):
    ircbot.irc.messaging.clearQueue(channelData.channel)
    channelData.sendMessage(
        'Cleared all queued messages for ' + channelData.channel[1:])
    return True

def commandAutoJoin(channelData, nick, message, msgParts, permissions):
    if len(msgParts) >= 2:
        removeMsgs = ['0', 'false', 'no', 'remove', 'rem', 'delete', 'del',
                      'leave', 'part']
        if msgParts[1].lower() in removeMsgs:
            params = channelData, nick
            threading.Thread(target=threadDeleteAutoJoin, args=params).start()
            return True
    params = channelData, nick
    threading.Thread(target=threadInsertAutoJoin, args=params).start()
    return True

def threadInsertAutoJoin(channelData, nick):
    with database.factory.getDatabase() as db:
        result = db.saveAutoJoin(nick)
    
    wasInChat = ('#' + nick) in ircbot.irc.channels
    if not wasInChat:
        ircbot.irc.joinChannel(nick)
    
    if result and not wasInChat:
        channelData.sendMessage(
            'Auto join for ' + nick + ' is now enabled and joined ' +
            nick + ' chat')
    elif result:
        channelData.sendMessage('Auto join for ' + nick + ' is now enabled')
    elif not wasInChat:
        channelData.sendMessage(
            'Auto join for ' + nick + ' is already enabled but now joined ' +
            nick + ' chat')
    else:
        channelData.sendMessage(
            'Auto join for ' + nick + ' is already enabled and already in '
            'chat')

def threadDeleteAutoJoin(channelData, nick):
    with database.factory.getDatabase() as db:
        result = db.discardAutoJoin(nick)
        if result:
            channelData.sendMessage(
                'Auto join for ' + nick + ' is now disabled')
        else:
            channelData.sendMessage(
                'Auto join for ' + nick + ' was never enabled')
