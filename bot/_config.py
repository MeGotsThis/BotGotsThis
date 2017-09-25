import configparser
import os

import aiofiles

from typing import Dict, List  # noqa: F401


class BotConfig:
    def __init__(self) -> None:
        self.development: bool = False

        self.botnick: str = ''
        self.password: str = ''
        self.owner: str = ''

        self.awsServer: str = ''
        self.awsPort: int = 0

        self.messageLimit: int = 500
        self.modLimit: int = 100
        self.modSpamLimit: int = 100
        self.publicLimit: float = 20
        self.publicDelay: float = 1
        self.messageSpan: float = 30
        self.whiperLimit: float = 100
        self.whiperSpan: float = 30

        self.customMessageCooldown: float = 5
        self.customMessageUserCooldown: float = 20
        self.customMessageUrlTimeout: float = 5

        self.spamModeratorCooldown: float = 20

        self.warningDuration: float = 20
        self.moderatorDefaultTimeout: List[int] = [0, 0, 0]

        self.httpTimeout: float = 60

        self.joinLimit: int = 50
        self.joinPerSecond: float = 15

        self.database: Dict[str, str] = {
            'main': '',
            'oauth': '',
            'timeout': '',
            'timezone': '',
        }

        self.connections: Dict[str, int] = {
            'main': 10,
            'oauth': 10,
            'timeout': 10,
            'timezone': 10,
        }

        self.pkgs: List[str] = ['botgotsthis']

        self.twitchClientId: str = ''

        self.ircLogFolder: str = ''
        self.exceptionLog: str = ''

    async def read_config(self) -> None:
        ini: configparser.ConfigParser
        if os.path.isfile('twitch.ini'):
            ini = configparser.ConfigParser()
            async with aiofiles.open('twitch.ini', 'r',
                                     encoding='utf-8') as file:
                ini.read_string(await file.read(None))

            self.botnick = str(ini['BOT']['botnick']).lower()
            self.password = str(ini['BOT']['password'])
            self.owner = str(ini['BOT']['owner']).lower()

        if os.path.isfile('config.ini'):
            ini = configparser.ConfigParser()
            async with aiofiles.open('config.ini', 'r',
                                     encoding='utf-8') as file:
                ini.read_string(await file.read(None))

            self.awsServer = str(ini['TWITCH']['awsServer'])
            self.awsPort = int(ini['TWITCH']['awsPort'])

            self.development = bool(int(ini['BOT']['development']))

            self.messageLimit = int(ini['BOT']['messageLimit'])
            self.modLimit = min(int(ini['BOT']['modLimit']), 100)
            self.modSpamLimit = min(int(ini['BOT']['modSpamLimit']), 100)
            self.publicLimit = min(int(ini['BOT']['publicLimit']), 20)
            self.publicDelay = float(ini['BOT']['publicDelay'])
            self.messageSpan = float(ini['BOT']['messageSpan'])
            self.whiperLimit = float(ini['BOT']['whiperLimit'])
            self.whiperSpan = float(ini['BOT']['whiperSpan'])

            f: float
            i: int

            f = float(ini['BOT']['customMessageCooldown'])
            self.customMessageCooldown = f
            if self.customMessageCooldown <= 0:
                self.customMessageCooldown = 20.0
            f = float(ini['BOT']['customMessageUserCooldown'])
            self.customMessageUserCooldown = f
            if self.customMessageUserCooldown <= 0:
                self.customMessageUserCooldown = 20.0
            f = float(ini['BOT']['customMessageUrlTimeout'])
            self.customMessageUrlTimeout = f
            if self.customMessageUrlTimeout <= 0:
                self.customMessageUrlTimeout = 5.0

            f = float(ini['BOT']['spamModeratorCooldown'])
            self.spamModeratorCooldown = f
            if self.spamModeratorCooldown <= 0:
                self.spamModeratorCooldown = 20.0

            self.warningDuration = float(ini['BOT']['warningDuration'])
            if self.warningDuration <= 0:
                self.warningDuration = 20.0
            self.moderatorDefaultTimeout = [0, 0, 0]
            i = int(ini['BOT']['moderatorDefaultTimeout0'])
            self.moderatorDefaultTimeout[0] = i
            if self.moderatorDefaultTimeout[0] <= 0:
                self.moderatorDefaultTimeout[0] = 0
            i = int(ini['BOT']['moderatorDefaultTimeout1'])
            self.moderatorDefaultTimeout[1] = i
            if self.moderatorDefaultTimeout[1] <= 0:
                self.moderatorDefaultTimeout[1] = 0
            i = int(ini['BOT']['moderatorDefaultTimeout2'])
            self.moderatorDefaultTimeout[2] = i
            if self.moderatorDefaultTimeout[2] <= 0:
                self.moderatorDefaultTimeout[2] = 0

            self.joinLimit = min(int(ini['BOT']['joinLimit']), 50)
            self.joinPerSecond = float(ini['BOT']['joinPerSecond'])
            if self.joinPerSecond <= 0:
                self.joinPerSecond = 20.0

            self.httpTimeout = float(ini['BOT']['httpTimeout'])

            self.ircLogFolder = str(ini['BOT']['ircLogFolder'])
            self.exceptionLog = str(ini['BOT']['exceptionLog'])
            if self.ircLogFolder:
                if not os.path.isdir(self.ircLogFolder):
                    os.mkdir(self.ircLogFolder)

        if os.path.isfile('pkg.ini'):
            ini = configparser.ConfigParser()
            async with aiofiles.open('pkg.ini', 'r',
                                     encoding='utf-8') as file:
                ini.read_string(await file.read(None))

            self.pkgs.clear()
            option: str
            _value: str
            for option, _value in ini.items('PKG'):  # type: ignore
                if ini.getboolean('PKG', option):
                    self.pkgs.append(option)
            if 'botgotsthis' not in self.pkgs:
                self.pkgs.append('botgotsthis')

        if os.path.isfile('database.ini'):
            ini = configparser.ConfigParser()
            async with aiofiles.open('database.ini', 'r',
                                     encoding='utf-8') as file:
                ini.read_string(await file.read(None))

            for s in ['main', 'oauth', 'timeout', 'timezone']:
                self.database[s] = str(ini['DATABASE'][s])
                if ini['CONNECTIONS'][s]:
                    i = int(ini['CONNECTIONS'][s])
                    if i:
                        self.connections[s] = i

        if os.path.isfile('twitchApi.ini'):
            ini = configparser.ConfigParser()
            async with aiofiles.open('twitchApi.ini', 'r',
                                     encoding='utf-8') as file:
                ini.read_string(await file.read(None))

            self.twitchClientId = str(ini['twitch']['twitchClientID'])
