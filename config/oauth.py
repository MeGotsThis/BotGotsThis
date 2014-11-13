import json

def getOAuthToken(channel):
    with open('oauth.json', encoding='utf-8') as file:
        oauth = json.load(file)
    if channel in oauth:
        return oauth[channel]
    return None
