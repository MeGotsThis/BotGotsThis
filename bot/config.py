from typing import List
import configparser
import os

development = False  # type: bool

botnick = ''  # type: str
password = ''  # type: str
owner = ''  # type: str

awsServer = ''  # type: str
awsPort = 0  # type: int

messageLimit = 500  # type: int
modLimit = 100  # type: int
modSpamLimit = 100  # type: int
publicLimit = 20  # type: int
publicDelay = 1  # type: float
messageSpan = 30  # type: float
whiperLimit = 100  # type: float
whiperSpan = 30  # type: float

customMessageCooldown = 5  # type: float
customMessageUserCooldown = 20  # type: float
customMessageUrlTimeout = 5  # type: float

spamModeratorCooldown = 20  # type: float

warningDuration = 20  # type: float
moderatorDefaultTimeout = [0, 0, 0]  # type: List[int]

joinLimit = 50  # type: int
joinPerSecond = 15  # type: float

ircLogFolder = ''  # type: str
exceptionLog = ''  # type: str


if os.path.isfile('twitch.ini'):
    ini = configparser.ConfigParser()
    ini.read('twitch.ini')

    botnick = str(ini['BOT']['botnick']).lower()
    password = str(ini['BOT']['password'])
    owner = str(ini['BOT']['owner']).lower()

if os.path.isfile('config.ini'):
    ini = configparser.ConfigParser()
    ini.read('config.ini')

    awsServer = str(ini['TWITCH']['awsServer'])
    awsPort = int(ini['TWITCH']['awsPort'])

    development = bool(int(ini['BOT']['development']))

    messageLimit = int(ini['BOT']['messageLimit'])
    modLimit = min(int(ini['BOT']['modLimit']), 100)
    modSpamLimit = min(int(ini['BOT']['modSpamLimit']), 100)
    publicLimit = min(int(ini['BOT']['publicLimit']), 20)
    publicDelay = float(ini['BOT']['publicDelay'])
    messageSpan = float(ini['BOT']['messageSpan'])
    whiperLimit = float(ini['BOT']['whiperLimit'])
    whiperSpan = float(ini['BOT']['whiperSpan'])

    customMessageCooldown = float(ini['BOT']['customMessageCooldown'])
    if customMessageCooldown <= 0:
        customMessageCooldown = 20
    customMessageUserCooldown = float(ini['BOT']['customMessageUserCooldown'])
    if customMessageUserCooldown <= 0:
        customMessageUserCooldown = 20
    customMessageUrlTimeout = float(ini['BOT']['customMessageUrlTimeout'])
    if customMessageUrlTimeout <= 0:
        customMessageUrlTimeout = 5

    spamModeratorCooldown = float(ini['BOT']['spamModeratorCooldown'])
    if spamModeratorCooldown <= 0:
        spamModeratorCooldown = 20

    warningDuration = float(ini['BOT']['warningDuration'])
    if warningDuration <= 0:
        warningDuration = 20
    moderatorDefaultTimeout = [0, 0, 0]
    moderatorDefaultTimeout[0] = int(ini['BOT']['moderatorDefaultTimeout0'])
    if moderatorDefaultTimeout[0] <= 0:
        moderatorDefaultTimeout[0] = 0
    moderatorDefaultTimeout[1] = int(ini['BOT']['moderatorDefaultTimeout1'])
    if moderatorDefaultTimeout[1] <= 0:
        moderatorDefaultTimeout[1] = 0
    moderatorDefaultTimeout[2] = int(ini['BOT']['moderatorDefaultTimeout2'])
    if moderatorDefaultTimeout[2] <= 0:
        moderatorDefaultTimeout[2] = 0

    joinLimit = min(int(ini['BOT']['joinLimit']), 50)
    joinPerSecond = float(ini['BOT']['joinPerSecond'])
    joinPerSecond = joinPerSecond if joinPerSecond > 0 else 20

    ircLogFolder = str(ini['BOT']['ircLogFolder'])
    exceptionLog = str(ini['BOT']['exceptionLog'])
    if ircLogFolder and not os.path.isdir(ircLogFolder):
        os.mkdir(ircLogFolder)
