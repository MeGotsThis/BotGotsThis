import bot.config
from bot import utils
from bot.twitchmessage import IrcMessage, IrcMessageTagsReadOnly
from bot import data
from datetime import datetime
from typing import Callable, Dict, Mapping, List, Optional, Union
from . import channel, whisper
from .irccommand import clearchat, notice, userstate
try:
    from .private import ircmessage
except ImportError:
    from .public.default import ircmessage  # type: ignore

IrcHandler = Callable[['data.Socket', IrcMessage, datetime], None]
ircHandlers = {}  # type: Dict[Union[str, int], IrcHandler]

_logCommandPerChannel = [
    'PRIVMSG', 'NOTICE', 'MODE', 'JOIN', 'PART', 'USERSTATE', 'HOSTTARGET',
    'CLEARCHAT', 'ROOMSTATE', 'USERNOTICE',
    ]  # type: List[str]


def parseMessage(socket: 'data.Socket',
                 ircmsg: str,
                 timestamp: datetime) -> None:
    message = IrcMessage.fromMessage(ircmsg)  # type: IrcMessage
    if message.command in ircHandlers:
        ircHandlers[message.command](socket, message, timestamp)

    log_channel_message(message, timestamp)

    ircmessage.parseMessage(socket, ircmsg, timestamp)


def registerIrc(command: Union[str, int]) -> Callable[[IrcHandler], IrcHandler]:
    def decorator(func: IrcHandler) -> IrcHandler:
        ircHandlers[command] = func
        return func
    return decorator


@registerIrc('PRIVMSG')
def irc_privmsg(
        socket: 'data.Socket',
        message: IrcMessage,
        timestamp: datetime) -> None:
    channels = socket.channels  # type: Mapping[str, data.Channel]
    nick = message.prefix.nick  # type: Optional[str]
    where = message.params.middle  # type: str
    msg = message.params.trailing  # type: Optional[str]
    if where[0] == '#' and where[1:] in channels:
        channel.parse(channels[where[1:]], message.tags, nick, msg, timestamp)
    if where[0] == '#':
        utils.logIrcMessage(where + '#msg.log', nick + ': ' + msg, timestamp)
    if bot.config.botnick in msg.lower().split():
        utils.logIrcMessage(bot.config.botnick + '-Mentions.log',
                            nick + ' -> ' + where + ': ' + msg, timestamp)


@registerIrc('WHISPER')
def irc_whisper(
        socket: 'data.Socket',
        message: IrcMessage,
        timestamp: datetime) -> None:
    tags = message.tags  # type: IrcMessageTagsReadOnly
    nick = message.prefix.nick  # type: Optional[str]
    msg = message.params.trailing  # type: Optional[str]
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
        socket: 'data.Socket',
        message: IrcMessage,
        timestamp: datetime) -> None:
    channels = socket.channels  # type: Mapping[str, data.Channel]
    nick = None  # type: Optional[str]
    chan = None  # type: Optional[data.Channel]
    msg = message.params.trailing  # type: Optional[str]
    if message.prefix.nick is not None:
        nick = message.prefix.nick
    where = message.params.middle  # type: Optional[str]
    if where[0] == '#' and where[1:] in channels:
        chan = channels[where[1:]]
    if where[0] == '#':
        utils.logIrcMessage(where + '#notice.log', msg, timestamp)
    notice.parse(message.tags, chan, nick, msg)


@registerIrc('CLEARCHAT')
def irc_clearchat(
        socket: 'data.Socket',
        message: IrcMessage,
        timestamp: datetime) -> None:
    channels = socket.channels  # type: Mapping[str, data.Channel]
    nick = None  # type: Optional[str]
    chan = None  # type: Optional[data.Channel]
    if message.params.trailing is not None:
        nick = message.params.trailing
    where = message.params.middle  # type: Optional[str]
    if where[0] == '#' and where[1:] in channels:
        chan = channels[where[1:]]
    if where[0] == '#':
        utils.logIrcMessage(where + '#clearchat.log',
                            nick if nick else '#chat', timestamp)
    clearchat.parse(chan, nick)


@registerIrc('ROOMSTATE')
def irc_roomstate(
        socket: 'data.Socket',
        message: IrcMessage,
        timestamp: datetime) -> None:
    where = message.params.middle  # type: Optional[str]
    if where[0] == '#':
        utils.logIrcMessage(where + '#roomstate.log', str(message), timestamp)


@registerIrc('HOSTTARGET')
def irc_hosttarget(
        socket: 'data.Socket',
        message: IrcMessage,
        timestamp: datetime) -> None:
    where = message.params.middle  # type: Optional[str]
    if where[0] == '#':
        utils.logIrcMessage(where + '#hosttarget.log', str(message), timestamp)


@registerIrc('MODE')
def irc_mode(
        socket: 'data.Socket',
        message: IrcMessage,
        timestamp: datetime) -> None:
    channels = socket.channels  # type: Mapping[str, data.Channel]
    where, mode, nick = message.params.middle.split()  # type: str, str, str
    if where[0] == '#' and where[1:] in channels:
        if mode == '+o':
            channels[where[1:]].ircOps.add(nick)
        if mode == '-o':
            channels[where[1:]].ircOps.discard(nick)


@registerIrc('JOIN')
def irc_join(
        socket: 'data.Socket',
        message: IrcMessage,
        timestamp: datetime) -> None:
    channels = socket.channels  # type: Mapping[str, data.Channel]
    where = message.params.middle  # type: str
    nick = message.prefix.nick  # type: str
    if where[0] == '#' and where[1:] in channels:
        channels[where[1:]].ircUsers.add(nick)


@registerIrc(353)
def irc_353(
        socket: 'data.Socket',
        message: IrcMessage,
        timestamp: datetime) -> None:
    channels = socket.channels  # type: Mapping[str, data.Channel]
    where = message.params.middle.split()[-1]  # type: str
    nicks = message.params.trailing.split(' ')  # type: List[str]
    if where[0] == '#':
        utils.logIrcMessage(where + '#full.log', '< ' + str(message),
                            timestamp)
        if where[1:] in channels:
            channels[where[1:]].ircUsers.update(nicks)


@registerIrc(366)
def irc_366(
        socket: 'data.Socket',
        message: IrcMessage,
        timestamp: datetime) -> None:
    where = message.params.middle.split()[-1]  # type: str
    if where[0] == '#':
        utils.logIrcMessage(where + '#full.log', '< ' + str(message),
                            timestamp)


@registerIrc('PART')
def irc_part(
        socket: 'data.Socket',
        message: IrcMessage,
        timestamp: datetime) -> None:
    channels = socket.channels  # type: Mapping[str, data.Channel]
    where = message.params.middle  # type: Optional[str]
    nick = message.prefix.nick  # type: Optional[str]
    if where[0] == '#' and where[1:] in channels:
        channels[where[1:]].ircUsers.discard(nick)


@registerIrc('PING')
def irc_ping(
        socket: 'data.Socket',
        message: IrcMessage,
        timestamp: datetime) -> None:
    if message.params.trailing is not None:
        socket.ping(message.params.trailing)


@registerIrc('PONG')
def irc_pong(
        socket: 'data.Socket',
        message: IrcMessage,
        timestamp: datetime) -> None:
    if (message.prefix is not None
            and message.prefix.servername is not None
            and message.prefix.servername == 'tmi.twitch.tv'
            and not message.params.isEmpty
            and message.params.middle == 'tmi.twitch.tv'
            and message.params.trailing == bot.config.botnick):
        socket.lastPing = timestamp


@registerIrc('USERSTATE')
def irc_userstate(
        socket: 'data.Socket',
        message: IrcMessage,
        timestamp: datetime) -> None:
    channels = socket.channels  # type: Mapping[str, data.Channel]
    where = message.params.middle  # type:str
    if where[0] == '#':
        utils.logIrcMessage(where + '#userstate.log', '< ' + str(message),
                            timestamp)
    if where[0] == '#' and where[1:] in channels:
        userstate.parse(channels[where[1:]], message.tags)


def log_channel_message(message: IrcMessage,
                        timestamp: datetime):
    if message.command in _logCommandPerChannel:
        where = message.params.middle.split(None, 1)[0]
        if where[0] == '#':
            utils.logIrcMessage(where + '#full.log', '< ' + str(message),
                                timestamp)
