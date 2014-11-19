import ircbot.twitchApi
import configparser

ini = configparser.ConfigParser()
ini.read('twitchApi.ini')

response, data = ircbot.twitchApi.twitchCall(
    None, 'POST', '/kraken/oauth2/token/',
    headers = {'Content-Type': 'application/x-www-form-urlencoded'},
    data = {
        'client_id': ini['twitch']['twitchClientID'],
        'client_secret': ini['twitch']['twitchSecret'],
        'grant_type': 'authorization_code',
        'redirect_uri': ini['twitch']['redirectUri'],
        'code': '',
        })

print(data)
input()
