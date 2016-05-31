from bot import globals
import bot.error

messageLimit = 'Your message was not sent because you are '
messageLimit += 'sending messages too quickly.'
messageIdentical = 'Your message was not sent because it is identical to the '
messageIdentical += 'previous one you sent, less than 30 seconds ago.'

def parse(chat, nick, message):
    if message == 'Login unsuccessful':
        raise bot.error.LoginUnsuccessfulException()
    if message.startswith('You are permanently banned from talking in '):
        chat.isMod = False
        globals.messaging.clearQueue(chat.channel)
