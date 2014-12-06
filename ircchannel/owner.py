from config import config
import database.factory
import ircbot.irc
import datetime
import time
import sys

def commandExit(channelData, nick, message, msgParts, permissions):
    channelData.sendMessage('Goodbye Keepo', 0)
    time.sleep(0.5)
    for channel in set(ircbot.irc.channels.keys()):
        ircbot.irc.partChannel(channel)
    ircbot.irc.messaging.running = False
    return True

def commandSay(channelData, nick, message, msgParts, permissions):
    if (permissions['owner'] and permissions['ownerChan']):
        msgParts = message.split(None, 2)
        if msgParts[1][0] != '#':
            msgParts[1] = '#' + msgParts[1]
        if msgParts[1] in ircbot.irc.channels:
            ircbot.irc.channels[msgParts[1]].sendMessage(msgParts[2])
        return True
    return False

def commandJoin(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    chan = msgParts[1].lower()
    if chan[0] != '#':
        chan = '#' + chan
    if ircbot.irc.joinChannel(chan):
        channelData.sendMessage('Joining ' + chan[1:])
    else:
        channelData.sendMessage('Already joined ' + chan[1:])
    return True

def commandPart(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    chan = msgParts[1].lower()
    if chan[0] != '#':
        chan = '#' + chan
    ircbot.irc.partChannel(chan)
    channelData.sendMessage('Leaving ' + chan[1:])
    return True

def commandEmptyAll(channelData, nick, message, msgParts, permissions):
    ircbot.irc.messaging.clearAllQueue()
    channelData.sendMessage('Cleared all queued msgs')
    return True

def commandEmpty(channelData, nick, message, msgParts, permissions):
    if msgParts[1][0] != '#':
        msgParts[1] = '#' + msgParts[1]
    ircbot.irc.messaging.clearQueue(msgParts[1])
    channelData.sendMessage(
        'Cleared all queued messages for ' + msgParts[1][1:])
    return True

def commandManageBot(channelData, nick, message, msgParts, permissions):
    if len(msgParts) < 2:
        return False
    if msgParts[1] == 'autojoin':
        if len(msgParts) < 4:
            return False
        msgParts[3] = msgParts[3].lower()
        if msgParts[2] in ['add', 'insert', 'join']:
            with database.factory.getDatabase() as db:
                result = db.saveAutoJoin(msgParts[3])
                
            wasInChat = ('#' + msgParts[3]) in ircbot.irc.channels
            if not wasInChat:
                ircbot.irc.joinChannel(msgParts[3])
            
            if result and not wasInChat:
                channelData.sendMessage(
                    'Auto join for ' + msgParts[3] + ' is now enabled and '
                    'joined ' + msgParts[3] + ' chat')
            elif result:
                channelData.sendMessage(
                    'Auto join for ' + msgParts[3] + ' is now enabled')
            elif not wasInChat:
                channelData.sendMessage(
                    'Auto join for ' + msgParts[3] + ' is already enabled but '
                    'now joined ' + msgParts[3] + ' chat')
            else:
                channelData.sendMessage(
                    'Auto join for ' + nick + ' is already enabled and '
                    'already in chat')
            return True
        if msgParts[2] in ['del', 'delete', 'rem', 'remove', 'remove']:
            with database.factory.getDatabase() as db:
                result = db.discardAutoJoin(msgParts[3])
                if result:
                    channelData.sendMessage(
                        'Auto join for ' + msgParts[3] + ' is now disabled')
                else:
                    channelData.sendMessage(
                        'Auto join for ' + msgParts[3] + ' was never enabled')
            return True
        if msgParts[2] in ['pri', 'priority']:
            try:
                priority = int(msgParts[4])
            except Exception:
                priority = 0
            with database.factory.getDatabase() as db:
                result = db.setAutoJoinPriority(msgParts[3], priority)
                if result:
                    channelData.sendMessage(
                        'Auto join for ' + msgParts[3] + ' is set to '
                        'priority ' + str(priority))
                else:
                    channelData.sendMessage(
                        'Auto join for ' + msgParts[3] + ' was never enabled')
            return True
    if msgParts[1] == 'listchats':
        channels = [c[1:] for c in ircbot.irc.channels.keys()]
        channelData.sendMessage('Twitch Chats: ' + ', '.join(channels))
    return True
