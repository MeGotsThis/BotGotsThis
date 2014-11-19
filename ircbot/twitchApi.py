import config.oauth
import urllib.parse
import http.client

def twitchCall(channel, method, uri, headers={}, data=None):
    conn = http.client.HTTPSConnection('api.twitch.tv')
    
    token = config.oauth.getOAuthToken(channel)
    if token is not None:
        headers['Authorization'] = 'OAuth ' + token
    headers['Accept'] = 'application/vnd.twitchtv.v2+json'
    
    if data is not None:
        if type(data) is dict:
            data = urllib.parse.urlencode(data)
    
    conn.request(method, uri, data, headers)
    response = conn.getresponse()
    responseData = response.read()
    
    conn.close()
    
    return (response, responseData)