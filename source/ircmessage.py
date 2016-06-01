from . import channel, whisper
from .irccommand import clearchat, notice, userstate
try:
    from .private import ircmessage
except:
    from .public.default import ircmessage
from bot import config, utils
from bot.twitchmessage.ircmessage import IrcMessage
import bot.thread.socket
import datetime

_logCommandPerChannel = [
    'PRIVMSG', 'NOTICE', 'MODE', 'JOIN', 'PART', 'USERSTATE', 'HOSTTARGET',
    'CLEARCHAT', 'ROOMSTATE',
    ]

def parseMessage(socket, ircmsg, now):
    channels = socket.channels
    message = IrcMessage.fromMessage(ircmsg)
    if message.command == 'PRIVMSG':
        tags = message.tags
        nick = message.prefix.nick
        where = message.params.middle
        msg = message.params.trailing
        if where[0] == '#':
            utils.logIrcMessage(where + '#msg.log', nick + ': ' + msg, now)
        if config.botnick in msg.lower().split():
            utils.logIrcMessage(config.botnick + '-Mentions.log',
                                nick + ' -> ' + where + ': ' + msg, now)
        if where[0] == '#' and where[1:] in channels:
            chan = channels[where[1:]]
            channel.parse(chan, tags, nick, msg, now)
        
    if message.command == 'WHISPER':
        tags = message.tags
        nick = message.prefix.nick
        msg = message.params.trailing
        utils.logIrcMessage('@' + nick + '@whisper.log',
                            nick + ': ' + msg, now)
        utils.logIrcMessage(config.botnick + '-All Whisper.log',
                            nick + ' -> ' + config.botnick + ': ' + msg, now)
        utils.logIrcMessage(config.botnick + '-Raw Whisper.log',
                            '< ' + ircmsg, now)
        whisper.parse(tags, nick, msg, now)
        
    if message.command == 'NOTICE':
        nick = None
        chan = None
        msg = message.params.trailing
        if message.prefix.nick is not None:
            nick = message.prefix.nick
        where = message.params.middle
        if where[0] == '#' and where[1:] in channels:
            chan = channels[where[1:]]
        if where[0] == '#':
            utils.logIrcMessage(where + '#notice.log', msg, now)
        notice.parse(chan, nick, msg)
        
    if message.command == 'CLEARCHAT':
        nick = None
        chan = None
        if message.params.trailing is not None:
            nick = message.params.trailing
        where = message.params.middle
        if where[0] == '#' and where[1:] in channels:
            chan = channels[where[1:]]
        if where[0] == '#':
            who = nick if nick else '#chat'
            utils.logIrcMessage(where + '#clearchat.log', who, now)
        clearchat.parse(chan, nick)
    
    if message.command == 'ROOMSTATE':
        msg = message.params.trailing
        where = message.params.middle
        if where[0] == '#':
            utils.logIrcMessage(where + '#roomstate.log', str(message), now)
    
    if message.command == 'HOSTTARGET':
        msg = message.params.trailing
        where = message.params.middle
        if where[0] == '#':
            utils.logIrcMessage(where + '#hosttarget.log', str(message), now)
    
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
            utils.logIrcMessage(where + '#full.log', '< ' + ircmsg, now)
            if where[1:] in channels:
                channels[where[1:]].ircUsers.update(nicks)
        
    if message.command == 366:
        where = message.params.middle.split()[-1]
        if where[0] == '#':
            utils.logIrcMessage(where + '#full.log', '< ' + ircmsg, now)
        
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
        socket.lastPing = datetime.datetime.utcnow()
        
    if message.command == 'USERSTATE':
        where = message.params.middle
        if where[0] == '#':
            utils.logIrcMessage(where + '#userstate.log', str(message), now)
        if where[0] == '#' and where[1:] in channels:
            chan = channels[where[1:]]
            tags = message.tags
            userstate.parse(chan, tags)
        
    if message.command in _logCommandPerChannel:
        where = message.params.middle.split(None, 1)[0]
        if where[0] == '#':
            utils.logIrcMessage(where + '#full.log', '< ' + ircmsg, now)

    ircmessage.parseMessage(socket, ircmsg, now)
