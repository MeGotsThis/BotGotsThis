import asyncio

import bot
import bot.globals
import source.ircmessage

from collections import deque
from datetime import datetime, timedelta
from typing import Deque, Dict, List, Optional, Tuple, no_type_check


from bot import data, utils
from bot.coroutine import join
from bot.data.error import ConnectionReset, LoginUnsuccessful
from bot.twitchmessage import IrcMessage, IrcMessageParams


class ConnectionHandler:
    def __init__(self,
                 name: str,
                 server: str,
                 port: int) -> None:
        self._writeQueue: Deque[Tuple[Tuple[IrcMessage], dict]] = deque()
        self._name: str = name
        self._server: str = server
        self._port: int = port
        self._channels: Dict[str, data.Channel] = {}
        self._transport: Optional[asyncio.BaseTransport] = None
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._messaging: data.MessagingQueue = data.MessagingQueue()
        self.lastSentPing: datetime = datetime.max
        self.lastPing: datetime = datetime.max
        self.lastConnectAttempt: datetime = datetime.min

    @property
    def name(self) -> str:
        return self._name

    @property
    def server(self) -> str:
        return self._server

    @property
    def port(self) -> int:
        return self._port

    @property
    def address(self) -> Tuple[str, int]:
        return self._server, self._port

    @property
    def isConnected(self) -> bool:
        return self._transport is not None

    @property
    def channels(self) -> Dict[str, 'data.Channel']:
        return self._channels.copy()

    @property
    def messaging(self) -> 'data.MessagingQueue':
        return self._messaging

    @property
    def writeQueue(self) -> Deque[Tuple[Tuple[IrcMessage], dict]]:
        return self._writeQueue

    async def run_connection(self):
        name: str = self.name
        print('{time} Starting {name}'.format(time=utils.now(), name=name))
        while bot.globals.running:
            if not self.isConnected and not await self.connect():
                await asyncio.sleep(5)
                continue
            try:
                self.send_ping()
                self.flush_writes()
                await self.drain()
                try:
                    await asyncio.wait_for(self.read(), 0.01)
                except asyncio.TimeoutError:
                    pass
            except (ConnectionError, ConnectionReset):
                if self._transport is None:
                    self.disconnect()
            except LoginUnsuccessful:
                if self._transport is None:
                    self.disconnect()
                break

        print('{time} Ending {name}'.format(time=utils.now(), name=name))

    async def connect(self) -> Optional[bool]:
        if self._transport is not None:
            raise ConnectionError('connection already exists')

        now: datetime = utils.now()
        if now - self.lastConnectAttempt < timedelta(seconds=1):
            return None
        self.lastConnectAttempt = now

        try:
            reader: asyncio.StreamReader
            writer: asyncio.StreamWriter
            reader, writer = await asyncio.open_connection(*self.address)

            print('{time} {name} Connected {server}'.format(
                time=utils.now(), name=self.name, server=self.server))
            await self.login(writer)
            self._reader = reader
            self._writer = writer
            self._transport = writer.transport

            now = utils.now()
            self.lastSentPing = now
            self.lastPing = now
            join.connected(self)

            return True
        except ConnectionError:
            return False

    async def login(self, writer: asyncio.StreamWriter) -> None:
        if not isinstance(writer, asyncio.StreamWriter):
            raise TypeError()
        commands: List[IrcMessage] = [
            IrcMessage(None, None, 'PASS',
                       IrcMessageParams(bot.config.password or None)),
            IrcMessage(None, None, 'NICK',
                       IrcMessageParams(bot.config.botnick)),
            IrcMessage(None, None, 'USER',
                       IrcMessageParams(bot.config.botnick + ' 0 *',
                                        bot.config.botnick)),
            IrcMessage(None, None, 'CAP',
                       IrcMessageParams('REQ', 'twitch.tv/membership')),
            IrcMessage(None, None, 'CAP',
                       IrcMessageParams('REQ', 'twitch.tv/commands')),
            IrcMessage(None, None, 'CAP',
                       IrcMessageParams('REQ', 'twitch.tv/tags')),
            ]
        command: IrcMessage
        for command in commands:
            message: bytes = (str(command) + '\r\n').encode('utf-8')
            writer.write(message)
            self._log_write(command)
            await writer.drain()

    def disconnect(self):
        if self._transport is None:
            raise ConnectionError()
        self._transport.close()
        join.disconnected(self)
        self._transport = None
        self._reader = None
        self._writer = None
        self.lastConnectAttempt = utils.now()
        self.lastSentPing = datetime.max
        self.lastPing = datetime.max
        print('{time} {name} Disconnected {server}'.format(
            time=utils.now(), name=self.name, server=self._server))

    async def write(self,
              command: IrcMessage, *,
              channel: 'Optional[data.Channel]'=None,
              whisper: 'Optional[data.WhisperMessage]'=None) -> None:
        if not isinstance(command, IrcMessage):
            raise TypeError()
        if self._transport is None:
            raise ConnectionError()

        try:
            messageBytes: bytes = str(command).encode('utf-8')
            timestamp: datetime = utils.now()
            self._writer.write(messageBytes)
            self._writer.write(b'\r\n')
            await self._writer.drain()
            self._on_write(command, timestamp, channel=channel)
            # TODO: mypy fix in the future
            self._log_write(command, channel=channel, whisper=whisper,  # type: ignore
                            timestamp=timestamp)
        except:
            utils.logException()
            raise

    def _on_write(self,
                  command: IrcMessage,
                  timestamp: datetime, *,
                  channel: 'Optional[data.Channel]'=None) -> None:
        if command.command == 'PING':
            self.lastSentPing = timestamp
        if command.command == 'JOIN' and isinstance(channel, data.Channel):
            channel.onJoin()
            join.record_join()
            print('{time} Joined {channel} on {socket}'.format(
                time=timestamp, channel=channel.channel, socket=self.name))

    async def drain(self) -> None:
        if self._transport is None:
            raise ConnectionError()
        while self.writeQueue:
            item: Tuple[Tuple[IrcMessage], dict] = self.writeQueue.popleft()
            await self.write(*item[0], **item[1])

    async def read(self) -> None:
        if self._transport is None:
            raise ConnectionError()
        try:
            ircmsg: bytes = await self._reader.readuntil(b'\r\n')
        except ConnectionError:
            utils.logException()
            return

        try:
            ircmsg = ircmsg[:-2]
            if not ircmsg:
                return
            message: str = ircmsg.decode('utf-8')
            self._log_read(message)
            source.ircmessage.parseMessage(self, message, utils.now())
        except ConnectionReset:
            raise
        except LoginUnsuccessful:
            bot.globals.running = False
            raise

    def ping(self, message: str='ping') -> None:
        self.queue_write(IrcMessage(None, None, 'PONG',
                                    IrcMessageParams(None, message)),
                         prepend=True)
        self.lastPing = utils.now()

    def send_ping(self) -> None:
        now = utils.now()
        sinceLastSend: timedelta = now - self.lastSentPing
        sinceLast: timedelta = now - self.lastPing
        if sinceLastSend >= timedelta(minutes=1):
            self.queue_write(IrcMessage(None, None, 'PING',
                                        IrcMessageParams(bot.config.botnick)),
                             prepend=True)
            self.lastSentPing = now
        elif sinceLast >= timedelta(minutes=1, seconds=15):
            raise ConnectionError()

    def _log_read(self, message: str) -> None:
        file: str = '{nick}-{server}.log'.format(nick=bot.config.botnick,
                                                 server=self.name)
        utils.logIrcMessage(file, '< ' + message)

    # TODO: mypy fix in the future
    @no_type_check
    def _log_write(self,
                   command: IrcMessage, *,
                   channel: 'Optional[data.Channel]'=None,
                   whisper: 'Optional[data.WhisperMessage]'=None,
                   timestamp: Optional[datetime]=None) -> None:
        timestamp = timestamp or utils.now()
        if command.command == 'PASS':
            command = IrcMessage(command='PASS')
        files: List[str] = []
        logs: List[str] = []
        files.append('{bot}-{socket}.log'.format(bot=bot.config.botnick,
                                                 socket=self.name))
        logs.append('> ' + str(command))
        file: str
        log: str
        if whisper and channel:
            for file, log in zip(files, logs):
                utils.logIrcMessage(file, log, timestamp)
            raise ValueError()
        if whisper:
            files.append('@{nick}@whisper.log'.format(nick=whisper.nick))
            logs.append('{bot}: {message}'.format(bot=bot.config.botnick,
                                                  message=whisper.message))
            files.append(
                '{bot}-All Whisper.log'.format(bot=bot.config.botnick))
            logs.append(
                '{bot} -> {nick}: {message}'.format(
                    bot=bot.config.botnick, nick=whisper.nick,
                    message=whisper.message))
            files.append(
                '{bot}-Raw Whisper.log'.format(bot=bot.config.botnick))
            logs.append('> ' + str(command))
        if channel:
            files.append(
                '{channel}#full.log'.format(channel=channel.ircChannel))
            logs.append('> ' + str(command))
            if command.command == 'PRIVMSG':
                files.append(
                    '{channel}#msg.log'.format(channel=channel.ircChannel))
                logs.append(
                    '{bot}: {message}'.format(bot=bot.config.botnick,
                                              message=command.params.trailing))
        for file, log in zip(files, logs):
            utils.logIrcMessage(file, log, timestamp)

    # TODO: mypy fix in the future
    @no_type_check
    def queue_write(self,
                    message: IrcMessage, *,
                    channel: 'Optional[data.Channel]'=None,
                    whisper: 'Optional[data.WhisperMessage]'=None,
                    prepend: bool=False) -> None:
        if not isinstance(message, IrcMessage):
            raise TypeError()
        kwargs: dict = {}
        if channel:
            if not isinstance(channel, data.Channel):
                raise TypeError()
            kwargs['channel'] = channel
        if whisper:
            if not isinstance(whisper, data.WhisperMessage):
                raise TypeError()
            kwargs['whisper'] = whisper
        if channel and whisper:
            raise ValueError()
        item: Tuple[Tuple[IrcMessage], dict]
        item = (message,), kwargs
        if prepend:
            self.writeQueue.appendleft(item)
        else:
            self.writeQueue.append(item)

    def join_channel(self, channel: 'data.Channel') -> None:
        self._channels[channel.channel] = channel

    def part_channel(self, channel: 'data.Channel') -> None:
        if channel.channel not in self._channels:
            return
        self.queue_write(IrcMessage(None, None, 'PART',
                                    IrcMessageParams(channel.ircChannel)))
        del self._channels[channel.channel]

        join.on_part(channel.channel)
        print('{time} Parted {channel}'.format(
            time=utils.now(), channel=channel.channel))

    # TODO: mypy fix in the future
    @no_type_check
    def flush_writes(self) -> None:
        self.messaging.cleanOldTimestamps()
        whisperMessage: data.WhisperMessage
        for whisperMessage in iter(self.messaging.popWhisper, None):
            ircMsg: str = '.w {nick} {message}'.format(
                nick=whisperMessage.nick,
                message=whisperMessage.message)[:bot.config.messageLimit]
            self.queue_write(
                IrcMessage(None, None, 'PRIVMSG',
                           IrcMessageParams(
                               bot.globals.groupChannel.ircChannel, ircMsg)),
                whisper=whisperMessage)
        nessage: data.ChatMessage
        for message in iter(self.messaging.popChat, None):
            self.queue_write(
                IrcMessage(None, None, 'PRIVMSG',
                           IrcMessageParams(
                               message.channel.ircChannel,
                               message.message[:bot.config.messageLimit])),
                channel=message.channel)
