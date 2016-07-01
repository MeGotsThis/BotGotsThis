from . import data
from .thread import background as backgroundThread
from .thread.join import JoinThread
from .thread.socket import SocketsThread
from datetime import datetime
from typing import Any, Dict, List
from . import config

running = True  # type: bool

# Import some necessary libraries.
sockets = None  # type: SocketsThread

join = None  # type: JoinThread
groupChannel = None  # type: data.Channel

background = None  # type: backgroundThread.BackgroundTasker

clusters = {
    'aws': None,
    }  # type: Dict[str, data.Socket]
whisperCluster = 'aws'  # type: str

channels = {}  # type: Dict[str, data.Channel]
displayName = config.botnick  # type: str
isTwitchTurbo = False  # type: bool
isTwitchAdmin = False  # type: bool
isTwitchStaff = False  # type: bool
isGlobalMod = False  # type: bool
emoteset = [0]  # type: List[int]
globalEmotes = {
    25: 'Kappa',
    88: 'PogChamp',
    1902: 'Keepo',
    33: 'DansGame',
    34: 'SwiftRage',
    36: 'PJSalt',
    356: 'OpieOP',
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
    }  # type: Dict[int, str]
globalEmoteSets = {k: 0 for k, v in globalEmotes.items()}  # type: Dict[int, int]
globalEmotesCache = datetime.min  # type: datetime
globalSessionData = {}  # type: Dict[Any, Any]
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
    }  # type: Dict[int, str]
globalFfzEmotesCache = datetime.min  # type: datetime
globalBttvEmotes = {
    }  # type: Dict[str, str]
globalBttvEmotesCache = datetime.min  # type: datetime
