from bot import config, globals

def manageListChats(db, send, nick, message, msgParts):
    channels = [c for c in globals.channels.keys()]
    channels.sort()
    chanList = []
    length = 0
    while channels:
        chan = channels.pop(0)
        chanList.append(chan)
        if length:
            length += 2
        length += len(chan)
        if length >= config.messageLimit:
            if len(chanList) > 1:
                send('Twitch Chats: ' + ', '.join(chanList[:-1]))
                del chanList[:-1]
                length = len(chan)
            else:
                send('Twitch Chats: ' + ', '.join(chanList))
                chanList.clear()
                length = 0
    if chanList:
        send('Twitch Chats: ' + ', '.join(chanList))
    return True
