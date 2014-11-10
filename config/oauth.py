import json

def getOAuthToken(channel):
    with open('oauth.json') as file:
        oauth = json.load(file)
    if channel in oauth:
        return oauth[channel]
    return None
