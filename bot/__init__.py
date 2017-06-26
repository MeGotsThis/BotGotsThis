import configparser
import os

import aiofiles

from datetime import datetime

from typing import Any, Dict, Optional, List  # noqa: F401

from . import data  # noqa: F401
from .coroutine import connection  # noqa: F401


class BotConfig:
    def __init__(self):
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

        self.twitchClientId: str = ''

        self.ircLogFolder: str = ''
        self.exceptionLog: str = ''

    async def read_config(self) -> None:
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

        if os.path.isfile('database.ini'):
            ini = configparser.ConfigParser()
            async with aiofiles.open('database.ini', 'r',
                                     encoding='utf-8') as file:
                ini.read_string(await file.read(None))

            self.database['main'] = str(ini['DATABASE']['main'])
            self.database['oauth'] = str(ini['DATABASE']['oauth'])
            self.database['timeout'] = str(ini['DATABASE']['timeout'])
            self.database['timezone'] = str(ini['DATABASE']['timezone'])

        if os.path.isfile('twitchApi.ini'):
            ini = configparser.ConfigParser()
            async with aiofiles.open('twitchApi.ini', 'r',
                                     encoding='utf-8') as file:
                ini.read_string(await file.read(None))

            self.twitchClientId = str(ini['twitch']['twitchClientID'])


class BotGlobals:
    def __init__(self):
        self.running: bool = True

        self.groupChannel: 'data.Channel' = None

        self.clusters: Dict[str, 'connection.ConnectionHandler'] = {
            'aws': None,
        }
        self.whisperCluster: str = 'aws'

        self.channels: Dict[str, 'data.Channel'] = {}
        self.twitchId: Dict[str, Optional[str]] = {}
        self.twitchIdName: Dict[str, str] = {}
        self.twitchIdCache: Dict[str, datetime] = {}
        self.twitchCommunity: Dict[str, Optional[str]] = {}
        self.twitchCommunityId: Dict[str, str] = {}
        self.twitchCommunityCache: Dict[str, datetime] = {}
        self.displayName: str = ''
        self.isTwitchAdmin: bool = False
        self.isTwitchStaff: bool = False
        self.isGlobalMod: bool = False
        self.emoteset: List[int] = [0]
        self.globalEmotes: Dict[int, str] = {
            25: 'Kappa',
            88: 'PogChamp',
            1902: 'Keepo',
            33: 'DansGame',
            34: 'SwiftRage',
            36: 'PJSalt',
            356: 'OpieOP',
            41: 'Kreygasm',
            86: 'BibleThump',
            1906: 'SoBayed',
            9803: 'KAPOW',
            245: 'ResidentSleeper',
            65: 'FrankerZ',
            40: 'KevinTurtle',
            27301: 'HumbleLife',
            881: 'BrainSlug',
            96: 'BloodTrail',
            22998: 'panicBasket',
            167: 'WinWaker',
            171: 'TriHard',
            66: 'OneHand',
            9805: 'NightBat',
            28: 'MrDestructoid',
            1901: 'Kippa',
            1900: 'RalpherZ',
            1: ':)',
            2: ':(',
            8: ':o',
            5: ':z',
            7: 'B)',
            10: ':\\',
            11: ';)',
            13: ';P',
            12: ':P',
            14: 'R)',
            6: 'o_O',
            3: ':D',
            4: '>(',
            9: '<3',
        }
        self.globalEmoteSets: Dict[int, int] = {k: 0 for k, v in
                                                self.globalEmotes.items()}
        self.globalEmotesCache: datetime = datetime.min
        self.globalSessionData: Dict[Any, Any] = {}
        self.globalFfzEmotes: Dict[int, str] = {
            25927: 'CatBag',
            27081: 'ZreknarF',
            28136: 'LilZ',
            28138: 'ZliL',
            9: 'ZrehplaR',
            6: 'YooHoo',
            5: 'YellowFever',
            4: 'ManChicken',
            3: 'BeanieHipster',
        }
        self.globalFfzEmotesCache: datetime = datetime.min
        self.globalBttvEmotes: Dict[str, str] = {}
        self.globalBttvEmotesCache: datetime = datetime.min


config: BotConfig = BotConfig()
globals: BotGlobals = BotGlobals()
