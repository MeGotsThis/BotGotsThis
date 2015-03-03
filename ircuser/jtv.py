from config import config

messageLimit = 'Your message was not sent because you are '
messageLimit += 'sending messages too quickly.'
messageIdentical = 'Your message was not sent because it is identical to the '
messageIdentical = 'previous one you sent, less than 30 seconds ago.'

def parse(channelData, message):
    if message.startswith('The moderators of this room are: '):
        l = len('The moderators of this room are: ')
        mods = message[l:]
        for mod in mods.split(', '):
            mod = str(mod)
            channelData.addMod(mod)
    if message.startswith('SPECIALUSER'):
        user, usertype = message.split(' ')[1:3]
        user = str(user)
        usertype = str(usertype)
        if usertype == 'staff':
            channelData.addTwitchStaff(user)
        if usertype == 'admin':
            channelData.addTwitchAdmin(user)
        if usertype == 'global_mod':
            channelData.addGlobalMod(user)
        if usertype == 'subscriber':
            channelData.addSubscriber(user)
        if usertype == 'turbo':
            channelData.addTurboUser(user)
    if message.startswith('You are permanently banned from talking in '):
        channelData.removeMod(config.botnick.lower())
        channelData.sendMessage('.mods', 0)
    if message in [messageLimit, messageIdentical]:
        channelData.removeMod(config.botnick.lower())
        channelData.sendMessage('.mods', 0)
