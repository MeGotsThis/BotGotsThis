from bot import globals

def manageListChats(db, send, nick, message, msgParts):
    channels = [c for c in globals.channels.keys()]
    send('Twitch Chats: ' + ', '.join(channels))
    return True
