import importlib
from datetime import datetime
from typing import Any, Callable, Dict, Mapping, List, Optional, Union  # noqa: F401, E501

import bot
from bot import data, utils  # noqa: F401
from bot.coroutine import connection as connectionM  # noqa: F401
from bot.twitchmessage import IrcMessage, IrcMessageTagsReadOnly  # noqa: F401
from . import channel, whisper
from .irccommand import clearchat, notice, userstate

IrcHandler = Callable[['connectionM.ConnectionHandler', IrcMessage, datetime],
                      None]
ircHandlers: Dict[Union[str, int], IrcHandler] = {}

_logCommandPerChannel: List[str] = [
    'PRIVMSG', 'NOTICE', 'MODE', 'JOIN', 'PART', 'USERSTATE', 'HOSTTARGET',
    'CLEARCHAT', 'ROOMSTATE', 'USERNOTICE',
    ]


def parseMessage(connection: 'connectionM.ConnectionHandler',
                 ircmsg: str,
                 timestamp: datetime) -> None:
    message: IrcMessage = IrcMessage.fromMessage(ircmsg)
    if message.command in ircHandlers:
        ircHandlers[message.command](connection, message, timestamp)

    log_channel_message(message, timestamp)

    pkg: str
    for pkg in bot.globals.pkgs:
        ircmessage: Any
        ircmessage = importlib.import_module('pkg.' + pkg + '.ircmessage')
        ircmessage.parseMessage(connection, ircmsg, timestamp)


def registerIrc(command: Union[str, int]
                ) -> Callable[[IrcHandler], IrcHandler]:
    def decorator(func: IrcHandler) -> IrcHandler:
        ircHandlers[command] = func
        return func
    return decorator


@registerIrc('PRIVMSG')
def irc_privmsg(
        connection: 'connectionM.ConnectionHandler',
        message: IrcMessage,
        timestamp: datetime) -> None:
    channels: Mapping[str, data.Channel] = connection.channels
    nick: Optional[str] = message.prefix.nick
    where: str = message.params.middle
    msg: Optional[str] = message.params.trailing
    if where[0] == '#' and where[1:] in channels:
        channel.parse(channels[where[1:]], message.tags, nick, msg, timestamp)
    if where[0] == '#':
        utils.logIrcMessage(where + '#msg.log', nick + ': ' + msg, timestamp)
    if bot.config.botnick in msg.lower().split():
        utils.logIrcMessage(bot.config.botnick + '-Mentions.log',
                            nick + ' -> ' + where + ': ' + msg, timestamp)


@registerIrc('WHISPER')
def irc_whisper(
        connection: 'connectionM.ConnectionHandler',
        message: IrcMessage,
        timestamp: datetime) -> None:
    tags: IrcMessageTagsReadOnly = message.tags
    nick: Optional[str] = message.prefix.nick
    msg: Optional[str] = message.params.trailing
    utils.logIrcMessage(
        '@' + nick + '@whisper.log', nick + ': ' + msg, timestamp)
    utils.logIrcMessage(bot.config.botnick + '-All Whisper.log',
                        nick + ' -> ' + bot.config.botnick + ': ' + msg,
                        timestamp)
    utils.logIrcMessage(
        bot.config.botnick + '-Raw Whisper.log', '< ' + str(message),
        timestamp)
    whisper.parse(tags, nick, msg, timestamp)


@registerIrc('NOTICE')
def irc_notice(
        connection: 'connectionM.ConnectionHandler',
        message: IrcMessage,
        timestamp: datetime) -> None:
    channels: Mapping[str, data.Channel] = connection.channels
    nick: Optional[str] = None
    chan: Optional[data.Channel] = None
    msg: Optional[str] = message.params.trailing
    if message.prefix.nick is not None:
        nick = message.prefix.nick
    where: Optional[str] = message.params.middle
    if where[0] == '#' and where[1:] in channels:
        chan = channels[where[1:]]
    if where[0] == '#':
        utils.logIrcMessage(where + '#notice.log', msg, timestamp)
    notice.parse(message.tags, chan, nick, msg)


@registerIrc('CLEARCHAT')
def irc_clearchat(
        connection: 'connectionM.ConnectionHandler',
        message: IrcMessage,
        timestamp: datetime) -> None:
    channels: Mapping[str, data.Channel] = connection.channels
    nick: Optional[str] = None
    chan: Optional[data.Channel] = None
    if message.params.trailing is not None:
        nick = message.params.trailing
    where: Optional[str] = message.params.middle
    if where[0] == '#' and where[1:] in channels:
        chan = channels[where[1:]]
    if where[0] == '#':
        utils.logIrcMessage(where + '#clearchat.log',
                            nick if nick else '#chat', timestamp)
    clearchat.parse(chan, nick)


@registerIrc('ROOMSTATE')
def irc_roomstate(
        connection: 'connectionM.ConnectionHandler',
        message: IrcMessage,
        timestamp: datetime) -> None:
    where: Optional[str] = message.params.middle
    if where[0] == '#':
        utils.logIrcMessage(where + '#roomstate.log', str(message), timestamp)


@registerIrc('HOSTTARGET')
def irc_hosttarget(
        connection: 'connectionM.ConnectionHandler',
        message: IrcMessage,
        timestamp: datetime) -> None:
    where: Optional[str] = message.params.middle
    if where[0] == '#':
        utils.logIrcMessage(where + '#hosttarget.log', str(message), timestamp)


@registerIrc('MODE')
def irc_mode(
        connection: 'connectionM.ConnectionHandler',
        message: IrcMessage,
        timestamp: datetime) -> None:
    channels: Mapping[str, data.Channel] = connection.channels
    where: str
    mode: str
    nick: str
    where, mode, nick = message.params.middle.split()
    if where[0] == '#' and where[1:] in channels:
        if mode == '+o':
            channels[where[1:]].ircOps.add(nick)
        if mode == '-o':
            channels[where[1:]].ircOps.discard(nick)


@registerIrc('JOIN')
def irc_join(
        connection: 'connectionM.ConnectionHandler',
        message: IrcMessage,
        timestamp: datetime) -> None:
    channels: Mapping[str, data.Channel] = connection.channels
    where: str = message.params.middle
    nick: str = message.prefix.nick
    if where[0] == '#' and where[1:] in channels:
        channels[where[1:]].ircUsers.add(nick)


@registerIrc(353)
def irc_353(
        connection: 'connectionM.ConnectionHandler',
        message: IrcMessage,
        timestamp: datetime) -> None:
    channels: Mapping[str, data.Channel] = connection.channels
    where: str = message.params.middle.split()[-1]
    nicks: List[str] = message.params.trailing.split(' ')
    if where[0] == '#':
        utils.logIrcMessage(where + '#full.log', '< ' + str(message),
                            timestamp)
        if where[1:] in channels:
            channels[where[1:]].ircUsers.update(nicks)


@registerIrc(366)
def irc_366(
        connection: 'connectionM.ConnectionHandler',
        message: IrcMessage,
        timestamp: datetime) -> None:
    where: str = message.params.middle.split()[-1]
    if where[0] == '#':
        utils.logIrcMessage(where + '#full.log', '< ' + str(message),
                            timestamp)


@registerIrc('PART')
def irc_part(
        connection: 'connectionM.ConnectionHandler',
        message: IrcMessage,
        timestamp: datetime) -> None:
    channels: Mapping[str, data.Channel] = connection.channels
    where: Optional[str] = message.params.middle
    nick: Optional[str] = message.prefix.nick
    if where[0] == '#' and where[1:] in channels:
        channels[where[1:]].ircUsers.discard(nick)


@registerIrc('PING')
def irc_ping(
        connection: 'connectionM.ConnectionHandler',
        message: IrcMessage,
        timestamp: datetime) -> None:
    if message.params.trailing is not None:
        connection.ping(message.params.trailing)


@registerIrc('PONG')
def irc_pong(
        connection: 'connectionM.ConnectionHandler',
        message: IrcMessage,
        timestamp: datetime) -> None:
    if (message.prefix is not None
            and message.prefix.servername is not None
            and message.prefix.servername == 'tmi.twitch.tv'
            and not message.params.isEmpty
            and message.params.middle == 'tmi.twitch.tv'
            and message.params.trailing == bot.config.botnick):
        connection.lastPing = timestamp


@registerIrc('USERSTATE')
def irc_userstate(
        connection: 'connectionM.ConnectionHandler',
        message: IrcMessage,
        timestamp: datetime) -> None:
    channels: Mapping[str, data.Channel] = connection.channels
    where: str = message.params.middle
    if where[0] == '#':
        utils.logIrcMessage(where + '#userstate.log', '< ' + str(message),
                            timestamp)
    if where[0] == '#' and where[1:] in channels:
        userstate.parse(channels[where[1:]], message.tags)


def log_channel_message(message: IrcMessage,
                        timestamp: datetime) -> None:
    if message.command in _logCommandPerChannel:
        where = message.params.middle.split(None, 1)[0]
        if where[0] == '#':
            utils.logIrcMessage(where + '#full.log', '< ' + str(message),
                                timestamp)
