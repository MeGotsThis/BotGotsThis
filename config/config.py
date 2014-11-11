import configparser
import json

server = 'irc.twitch.tv'
eventServer = '199.9.252.26'
ini = configparser.ConfigParser()
ini.read('config.ini')
botnick = ini['BOT']['botnick'].lower()
password = ini['BOT']['password']
owner = ini['BOT']['owner'].lower()

modLimit = int(ini['BOT']['modLimit'])
modSpamLimit = int(ini['BOT']['modSpamLimit'])
publicLimit = int(ini['BOT']['publicLimit'])
publicDelay = float(ini['BOT']['publicDelay'])
messagePerSecond = float(ini['BOT']['messagePerSecond'])

exceptionLog = ini['BOT']['exceptionLog']

autoJoin = []
autoJoin.append('#' + botnick)
if owner:
    autoJoin.append('#' + owner)
with open('autoJoin.json') as file:
    autoJoin += json.load(file)
