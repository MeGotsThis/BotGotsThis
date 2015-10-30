from . import channel, whisper
from .irccommand import notice, userstate
from bot import config
from bot.twitchmessage.ircmessage import IrcMessage
import bot.thread.socket
import datetime

_logCommandPerChannel = [
    'PRIVMSG', 'NOTICE', 'MODE', 'JOIN', 'PART', 'USERSTATE', 'HOSTTARGET',
    'CLEARCHAT', 'ROOMSTATE',
    ]

def parseMessage(socket, ircmsg, now):
    channels = socket.channels
    message = IrcMessage(message=ircmsg)
    if message.command == 'PRIVMSG':
        tags = message.tags
        nick = message.prefix.nick
        where = message.params.middle
        msg = message.params.trailing
        if where[0] == '#' and nick != 'jtv':
            bot.thread.socket._logMessage(
                where + '#msg.log', nick + ': ' + msg, now)
        if config.botnick in msg.split():
            file = config.botnick + '-Mentions.log'
            bot.thread.socket._logMessage(
                file, nick + ' -> ' + where + ': ' + msg, now)
        if where[0] == '#' and where[1:] in channels:
            chan = channels[where[1:]]
            channel.parse(chan, tags, nick, msg)
        
    if message.command == 'WHISPER':
        tags = message.tags
        nick = message.prefix.nick
        msg = message.params.trailing
        file = '@' + nick + '@whisper.log'
        bot.thread.socket._logMessage(file, nick + ': ' + msg, now)
        file = config.botnick + '-All Whisper.log'
        bot.thread.socket._logMessage(
            file, nick + ' -> ' + config.botnick + ': ' + msg, now)
        file = config.botnick + '-Raw Whisper.log'
        bot.thread.socket._logMessage(file, '< ' + ircmsg, now)
        whisper.parse(tags, nick, msg)
        
    if (message.command == 'NOTICE' and message.prefix is not None and
        message.prefix.nick is not None and
        message.params.trailing is not None):
        notice.parse(socket, message.prefix.nick, message.params.trailing)
        
    if message.command == 'MODE':
        where, mode, nick = message.params.middle.split()
        if where[0] == '#' and where[1:] in channels:
            if mode == '+o':
                channels[where[1:]].ircOps.add(nick)
            if mode == '-o':
                channels[where[1:]].ircOps.discard(nick)
        
    if message.command == 'JOIN':
        where = message.params.middle
        nick = message.prefix.nick
        if where[0] == '#' and where[1:] in channels:
            channels[where[1:]].ircUsers.add(nick)
        
    if message.command == 353:
        where = message.params.middle.split()[-1]
        nicks = message.params.trailing.split(' ')
        if where[0] == '#':
            bot.thread.socket._logMessage(
                where + '#full.log', '< ' + ircmsg, now)
            if where[1:] in channels:
                channels[where[1:]].ircUsers.update(nicks)
        
    if message.command == 366:
        where = message.params.middle.split()[-1]
        if where[0] == '#':
            bot.thread.socket._logMessage(
                where + '#full.log', '< ' + ircmsg, now)
        
    if message.command == 'PART':
        where = message.params.middle
        nick = message.prefix.nick
        if where[0] == '#' and where[1:] in channels:
            channels[where[1:]].ircUsers.discard(nick)

    if message.command == 'PING' and message.params.trailing is not None:
        socket.ping(message.params.trailing)
        
    if (message.command == 'PONG' and message.prefix is not None and
        message.prefix.servername is not None and 
        message.prefix.servername == 'tmi.twitch.tv' and
        not message.params.isEmpty and
        message.params.middle == 'tmi.twitch.tv' and
        message.params.trailing == config.botnick):
        socket.lastPing = datetime.datetime.now()
        
    if message.command == 'USERSTATE':
        where = message.params.middle
        if where[0] == '#' and where[1:] in channels:
            chan = channels[where[1:]]
            tags = message.tags
            userstate.parse(chan, tags)
        
    if message.command in _logCommandPerChannel:
        where = message.params.middle.split(None, 1)[0]
        if where[0] == '#':
            bot.thread.socket._logMessage(
                where + '#full.log', '< ' + ircmsg, now)
