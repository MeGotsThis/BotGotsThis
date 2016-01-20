import configparser
import os.path
import json
import sys
import os

if not os.path.isfile('twitch.ini'):
    print('Missing twitch.ini')
    sys.exit(0)

if not os.path.isfile('config.ini'):
    print('Missing config.ini')
    sys.exit(0)

ini = configparser.ConfigParser()
ini.read('twitch.ini')

botnick = str(ini['BOT']['botnick']).lower()
password = str(ini['BOT']['password'])
owner = str(ini['BOT']['owner']).lower()

ini = configparser.ConfigParser()
ini.read('config.ini')

mainServer = str(ini['TWITCH']['mainServer'])
mainPort = int(ini['TWITCH']['mainPort'])
eventServer = str(ini['TWITCH']['eventServer'])
eventPort = int(ini['TWITCH']['eventPort'])
groupServer = str(ini['TWITCH']['groupServer'])
groupPort = int(ini['TWITCH']['groupPort'])

messageLimit = int(ini['BOT']['messageLimit'])
modLimit = min(int(ini['BOT']['modLimit']), 100)
modSpamLimit = min(int(ini['BOT']['modSpamLimit']), 100)
publicLimit = min(int(ini['BOT']['publicLimit']), 20)
publicDelay = float(ini['BOT']['publicDelay'])
messagePerSecond = float(ini['BOT']['messagePerSecond'])
messagePerSecond = messagePerSecond if messagePerSecond > 0 else 20

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
