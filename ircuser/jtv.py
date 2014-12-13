def parse(channelData, message):
    if message.startswith('The moderators of this room are: '):
        l = len('The moderators of this room are: ')
        mods = message[l:]
        for mod in mods.split(', '):
            channelData.addMod(mod)
    if message.startswith('SPECIALUSER'):
        _, user, type = message.split(' ')
        if type == 'staff':
            channelData.addTwitchStaff(user)
        if type == 'admin':
            channelData.addTwitchAdmin(user)
        if type == 'subscriber':
            channelData.addSubscriber(user)
        if type == 'turbo':
            channelData.addTurboUser(user)
