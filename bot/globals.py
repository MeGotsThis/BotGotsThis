from . import config
import datetime
import sys
import threading
import traceback

# Import some necessary libraries.
messaging = None

join = None
groupChannel = None

background = None

clusters = {
    'aws': None,
    }
channels = {}
displayName = config.botnick
isTwitchTurbo = False
isTwitchAdmin = False
isTwitchStaff = False
emoteset = [0]
globalEmotes = {
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
globalEmoteSets = { k: 0 for k, v in globalEmotes.items() }
globalEmotesCache = datetime.datetime.min
globalSessionData = {}
globalFfzEmotes = {
    25927: 'CatBag',
    27081: 'ZreknarF',
    28136: 'LilZ',
    28138: 'ZliL',
    9: 'ZrehplaR',
    6: 'YooHoo',
    5: 'YellowFever',
    4: 'ManChicken',
    3: 'BeanieHipster',
    }
globalFfzEmotesCache = datetime.datetime.min
