import configparser
import os.path
import json
import sys
import os

if not os.path.isfile('config.ini'):
    print('Missing config.ini')
    sys.exit(0)

ini = configparser.ConfigParser()
ini.read('config.ini')

mainServer = str(ini['TWITCH']['main'])
eventServer = str(ini['TWITCH']['event'])
groupServer = str(ini['TWITCH']['group'])

botnick = str(ini['BOT']['botnick']).lower()
password = str(ini['BOT']['password'])
owner = str(ini['BOT']['owner']).lower()

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

spamModeratorCooldown = float(ini['BOT']['spamModeratorCooldown'])
if spamModeratorCooldown <= 0:
    spamModeratorCooldown = 20

joinLimit = min(int(ini['BOT']['joinLimit']), 50)
joinPerSecond = float(ini['BOT']['joinPerSecond'])
joinPerSecond = joinPerSecond if joinPerSecond > 0 else 20

ircLogFolder = str(ini['BOT']['ircLogFolder'])
exceptionLog = str(ini['BOT']['exceptionLog'])
if ircLogFolder and not os.path.isdir(ircLogFolder):
    os.mkdir(ircLogFolder)
