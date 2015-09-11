import config.config
import database.factory
import ircbot.irc
import ircbot.twitchApi
import json

def botJoin(channel, sendMessage):
    with database.factory.getDatabase() as db:
        if db.isChannelBannedReason(channel[1:]):
            sendMessage('Chat ' + channel[1:] + ' is banned from joining')
            return True
        priority = db.getAutoJoinsPriority(channel[1:])
    priority = priority if priority is not None else float('inf')
    
    response, data = ircbot.twitchApi.twitchCall(
        None, 'GET', '/api/channels/' + channel[1:] + '/chat_properties')
    chatProperties = json.loads(data.decode('utf-8'))
    
    if chatProperties['eventchat']:
        server = ircbot.irc.eventChat
    else:
        server = ircbot.irc.mainChat
    if ircbot.irc.joinChannel(channel, priority, server):
        sendMessage('Joining ' + channel[1:])
    else:
        result = ircbot.irc.ensureServer(channel, priority, server)
        if result == ircbot.irc.ENSURE_CORRECT:
            sendMessage('Already joined ' + channel[1:])
        elif result == ircbot.irc.ENSURE_REJOIN_TO_MAIN:
            sendMessage('Moved ' + channel[1:] + ' to main chat server')
        elif result == ircbot.irc.ENSURE_REJOIN_TO_EVENT:
            sendMessage('Moved ' + channel[1:] + ' to event chat server')

def botPart(channel, sendMessage):
    if channel[1:] == config.config.botnick:
        return
    ircbot.irc.partChannel(channel)
    sendMessage('Leaving ' + channel[1:])

def botSay(channel, message):
    if channel in ircbot.irc.channels:
        ircbot.irc.channels[channel].sendMessage(message)

def botEmptyAll(sendMessage):
    ircbot.irc.messaging.clearAllQueue()
    sendMessage('Cleared all queued messages')

def botEmpty(channel, sendMessage):
    ircbot.irc.messaging.clearQueue(msgParts[1])
    sendMessage('Cleared all queued messages for ' + msgParts[1][1:])
