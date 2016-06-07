from typing import List
import configparser
import os
import sys

if not os.path.isfile('twitch.ini'):
    print('Missing twitch.ini')
    sys.exit(0)

if not os.path.isfile('config.ini'):
    print('Missing config.ini')
    sys.exit(0)

ini = configparser.ConfigParser()
ini.read('twitch.ini')

botnick = str(ini['BOT']['botnick']).lower()  # type: str
password = str(ini['BOT']['password'])  # type: str
owner = str(ini['BOT']['owner']).lower()  # type: str

ini = configparser.ConfigParser()
ini.read('config.ini')

awsServer = str(ini['TWITCH']['awsServer'])  # type: str
awsPort = int(ini['TWITCH']['awsPort'])  # type: int

messageLimit = int(ini['BOT']['messageLimit'])  # type: int
modLimit = min(int(ini['BOT']['modLimit']), 100)  # type: int
modSpamLimit = min(int(ini['BOT']['modSpamLimit']), 100)  # type: int
publicLimit = min(int(ini['BOT']['publicLimit']), 20)  # type: int
publicDelay = float(ini['BOT']['publicDelay'])  # type: float

customMessageCooldown = float(ini['BOT']['customMessageCooldown'])  # type: float
if customMessageCooldown <= 0:
    customMessageCooldown = 20
customMessageUserCooldown = float(ini['BOT']['customMessageUserCooldown'])  # type: float
if customMessageUserCooldown <= 0:
    customMessageUserCooldown = 20
customMessageUrlTimeout = float(ini['BOT']['customMessageUrlTimeout'])  # type: float
if customMessageUrlTimeout <= 0:
    customMessageUrlTimeout = 5

spamModeratorCooldown = float(ini['BOT']['spamModeratorCooldown'])  # type: float
if spamModeratorCooldown <= 0:
    spamModeratorCooldown = 20

warningDuration = float(ini['BOT']['warningDuration'])  # type: float
if warningDuration <= 0:
    warningDuration = 20
moderatorDefaultTimeout = [0, 0, 0]  # type: List[int]
moderatorDefaultTimeout[0] = int(ini['BOT']['moderatorDefaultTimeout0'])
if moderatorDefaultTimeout[0] <= 0:
    moderatorDefaultTimeout[0] = 0
moderatorDefaultTimeout[1] = int(ini['BOT']['moderatorDefaultTimeout1'])
if moderatorDefaultTimeout[1] <= 0:
    moderatorDefaultTimeout[1] = 0
moderatorDefaultTimeout[2] = int(ini['BOT']['moderatorDefaultTimeout2'])
if moderatorDefaultTimeout[2] <= 0:
    moderatorDefaultTimeout[2] = 0

joinLimit = min(int(ini['BOT']['joinLimit']), 50)  # type: int
joinPerSecond = float(ini['BOT']['joinPerSecond'])  # type: float
joinPerSecond = joinPerSecond if joinPerSecond > 0 else 20

ircLogFolder = str(ini['BOT']['ircLogFolder'])  # type: str
exceptionLog = str(ini['BOT']['exceptionLog'])  # type: str
if ircLogFolder and not os.path.isdir(ircLogFolder):
    os.mkdir(ircLogFolder)
