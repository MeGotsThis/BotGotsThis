from config import config
import ircbot.irc

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
    if message.startswith('EMOTESET'):
        user, emoteset = message.split(' ')[1:3]
        if user == config.botnick.lower():
            emoteset = emoteset[1:-1].split(',')
            emoteset = [int(i) for i in emoteset]
            # This is to remove twitch turbo emotes that are shared with
            # global emoticons
            if 33 in emoteset:
                emoteset.remove(33)
            if 42 in emoteset:
                emoteset.remove(42)
            # Add global emoticons
            emoteset.insert(0, 0)
            if ('emoteset' not in ircbot.irc.globalSessionData or
                ircbot.irc.globalSessionData['emoteset'] != emoteset):
                ircbot.irc.globalSessionData['emoteset'] = emoteset
                if 'globalEmotes' in ircbot.irc.globalSessionData:
                    del ircbot.irc.globalSessionData['globalEmotes']
                if 'globalEmotesCache' in ircbot.irc.globalSessionData:
                    del ircbot.irc.globalSessionData['globalEmotesCache']
    if message.startswith('You are permanently banned from talking in '):
        channelData.removeMod(config.botnick.lower())
        channelData.sendMessage('.mods', 0)
    if message in [messageLimit, messageIdentical]:
        channelData.removeMod(config.botnick.lower())
        channelData.sendMessage('.mods', 0)
