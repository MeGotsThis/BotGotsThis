from lib.api import twitch
from lib import database
import urllib.parse
import configparser
import json

ini = configparser.ConfigParser()
ini.read('twitchApi.ini')


try:
    returnUrl = input('Return URL -> ')

    parsedUrl = urllib.parse.urlparse(returnUrl)
    queryParts = urllib.parse.parse_qs(parsedUrl.query)

    if 'code' in queryParts and len(queryParts['code']):
        for code in queryParts['code']:
            response, data = twitch.api_call(
                None, 'POST', '/kraken/oauth2/token/',
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/vnd.twitchtv.v2+json',
                    },
                data={
                    'client_id': ini['twitch']['twitchClientID'],
                    'client_secret': ini['twitch']['twitchSecret'],
                    'grant_type': 'authorization_code',
                    'redirect_uri': ini['twitch']['redirectUri'],
                    'code': code,
                    })

            if response.status == 200:
                oauthTokens = json.loads(data.decode('utf-8'))
                token = oauthTokens['access_token']

                response, data = twitch.api_call(
                    None, 'GET', '/kraken/',
                    headers={
                        'Authorization': 'OAuth ' + token,
                        'Accept': 'application/vnd.twitchtv.v2+json',
                        })
                if response.status == 200:
                    tokenInfo = json.loads(data.decode('utf-8'))

                    with database.get_database(database.Schema.OAuth) as db:
                        db.saveBroadcasterToken(
                            tokenInfo['token']['user_name'].lower(), token)
                    print(
                        'Saved token for',
                        tokenInfo['token']['user_name'].lower())
                else:
                    print('Bad access token:', token)
            else:
                print('Bad code:', code)
except Exception as e:
    print(e)

print('Done')
input()
