from config import config
import ircbot.irc

messageLimit = 'Your message was not sent because you are '
messageLimit += 'sending messages too quickly.'
messageIdentical = 'Your message was not sent because it is identical to the '
messageIdentical += 'previous one you sent, less than 30 seconds ago.'

def parse(channelData, message):
    if message.startswith('You are permanently banned from talking in '):
        channelData.isMod = False
        ircbot.irc.messaging.clearQueue(channelData.channel)
    if message in [messageLimit, messageIdentical]:
        channelData.isMod = False
