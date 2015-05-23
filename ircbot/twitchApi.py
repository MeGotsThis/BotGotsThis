import config.oauth
import urllib.parse
import http.client
import ircbot.irc
import os.path
import configparser
import datetime
import json

def getTwitchClientId():
    if os.path.isfile('config.ini'):
        ini = configparser.ConfigParser()
        ini.read('config.ini')
        if 'twitch' in ini and 'twitchClientID' in ini['twitch']:
            return ini['twitch']['twitchClientID']
    return None

def twitchCall(channel, method, uri, headers={}, data=None):
    conn = http.client.HTTPSConnection('api.twitch.tv')
    
    if channel is not None and 'Authorization' not in headers:
        token = config.oauth.getOAuthToken(channel)
        if token is not None:
            headers['Authorization'] = 'OAuth ' + token
        headers['Accept'] = 'application/vnd.twitchtv.v3+json'
        clientId = getTwitchClientId()
        if clientId is not None:
            headers['Client-ID'] = clientId
    
    if data is not None:
        if type(data) is dict:
            data = urllib.parse.urlencode(data)
    
    conn.request(method, uri, data, headers)
    response = conn.getresponse()
    responseData = response.read()
    
    conn.close()
    
    return (response, responseData)

def getTwitchEmotes():
    if 'globalEmotes' not in ircbot.irc.globalSessionData:
        ircbot.irc.globalSessionData['globalEmotes'] = {
            25: 'Kappa',
            88: 'PogChamp',
            1902: 'Keepo',
            33: 'DansGame',
            34: 'SwiftRage',
            36: 'PJSalt',
            356: 'OpieOP',
            88: 'PogChamp',
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
    if 'globalEmotesCache' not in ircbot.irc.globalSessionData:
        dtmin = datetime.datetime.min
        ircbot.irc.globalSessionData['globalEmotesCache'] = dtmin
    
    currentTime = datetime.datetime.utcnow()
    emotes = ircbot.irc.globalSessionData['globalEmotes']
    since = currentTime - ircbot.irc.globalSessionData['globalEmotesCache']
    if since > datetime.timedelta(hours=1):
        emoteset = ['0']
        if 'emoteset' in ircbot.irc.globalSessionData:
            emoteset = [str(i) for i in
                        ircbot.irc.globalSessionData['emoteset']]
        response, data = twitchCall(
            None, 'GET',
            '/kraken/chat/emoticon_images?emotesets=' + ','.join(emoteset),
            headers = {
                'Accept': 'application/vnd.twitchtv.v3+json',
                })
        globalEmotes = json.loads(data.decode('utf-8'))['emoticon_sets']
        emotes = {}
        replaceGlobal = {
            1: ':)',
            2: ':(',
            3: ':D',
            4: '>(',
            5: ':z',
            6: 'o_O',
            7: 'B)',
            8: ':o',
            9: '<3',
            10: ':\\',
            11: ';)',
            12: ':P',
            13: ';P',
            14: 'R)',
            }
        for emoteSetId in globalEmotes:
            for emote in globalEmotes[emoteSetId]:
                if emote['id'] in replaceGlobal:
                    emotes[emote['id']] = replaceGlobal[emote['id']]
                else:
                    emotes[emote['id']] = emote['code']
        ircbot.irc.globalSessionData['globalEmotes'] = emotes
        ircbot.irc.globalSessionData['globalEmotesCache'] = currentTime
    return emotes
