from ...database.factory import getDatabase
from ...api import twitch
from bot import config, globals, utils
import json

def botJoin(channel, sendMessage):
    with getDatabase() as db:
        if db.isChannelBannedReason(channel[1:]):
            sendMessage('Chat ' + channel[1:] + ' is banned from joining')
            return True
        priority = db.getAutoJoinsPriority(channel[1:])
    priority = priority if priority is not None else float('inf')
    
    response, data = twitch.twitchCall(
        None, 'GET', '/api/channels/' + channel[1:] + '/chat_properties')
    chatProperties = json.loads(data.decode('utf-8'))
    
    if chatProperties['eventchat']:
        server = globals.eventChat
    else:
        server = globals.mainChat
    if utils.joinChannel(channel, priority, server):
        sendMessage('Joining ' + channel[1:])
    else:
        result = utils.ensureServer(channel, priority, server)
        if result == utils.ENSURE_CORRECT:
            sendMessage('Already joined ' + channel[1:])
        elif result == utils.ENSURE_REJOIN_TO_MAIN:
            sendMessage('Moved ' + channel[1:] + ' to main chat server')
        elif result == utils.ENSURE_REJOIN_TO_EVENT:
            sendMessage('Moved ' + channel[1:] + ' to event chat server')

def botPart(channel, sendMessage):
    if channel[1:] == config.botnick:
        return
    utils.partChannel(channel)
    sendMessage('Leaving ' + channel[1:])

def botSay(channel, message):
    if channel in globals.channels:
        globals.channels[channel].sendMessage(message)

def botEmptyAll(sendMessage):
    globals.messaging.clearAllQueue()
    sendMessage('Cleared all queued messages')

def botEmpty(channel, sendMessage):
    globals.messaging.clearQueue(msgParts[1])
    sendMessage('Cleared all queued messages for ' + msgParts[1][1:])
