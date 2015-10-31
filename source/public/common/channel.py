from ...database.factory import getDatabase
from ...api import twitch
from bot import config, globals, utils
import json

def botJoin(db, channel, sendMessage):
    if db.isChannelBannedReason(channel):
        sendMessage('Chat ' + channel + ' is banned from joining')
        return True
    priority = db.getAutoJoinsPriority(channel)
    priority = priority if priority is not None else float('inf')
    
    response, data = twitch.twitchCall(
        None, 'GET', '/api/channels/' + channel + '/chat_properties')
    chatProperties = json.loads(data.decode('utf-8'))
    
    if chatProperties['eventchat']:
        server = globals.eventChat
    else:
        server = globals.mainChat
    if utils.joinChannel(channel, priority, server):
        sendMessage('Joining ' + channel)
    else:
        result = utils.ensureServer(channel, priority, server)
        if result == utils.ENSURE_CORRECT:
            sendMessage('Already joined ' + channel)
        elif result == utils.ENSURE_REJOIN_TO_MAIN:
            sendMessage('Moved ' + channel + ' to main chat server')
        elif result == utils.ENSURE_REJOIN_TO_EVENT:
            sendMessage('Moved ' + channel + ' to event chat server')

def botPart(channel, sendMessage):
    if channel == config.botnick:
        return
    utils.partChannel(channel)
    sendMessage('Leaving ' + channel)

def botSay(channel, message):
    if channel in globals.channels:
        globals.channels[channel].sendMessage(message)

def botEmptyAll(sendMessage):
    globals.messaging.clearAllQueue()
    sendMessage('Cleared all queued messages')

def botEmpty(channel, sendMessage):
    globals.messaging.clearQueue(msgParts[1])
    sendMessage('Cleared all queued messages for ' + msgParts[1])
