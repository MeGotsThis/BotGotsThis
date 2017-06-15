import bot.config
from . import data
from .coroutine import connection
from datetime import datetime
from typing import Any, Dict, Optional, List


running: bool = True

groupChannel: 'data.Channel' = None

clusters: Dict[str, 'connection.ConnectionHandler'] = {
    'aws': None,
    }
whisperCluster: str = 'aws'

channels: Dict[str, 'data.Channel'] = {}
twitchId: Dict[str, Optional[str]] = {}
twitchIdName: Dict[str, str] = {}
twitchIdCache: Dict[str, datetime] = {}
twitchCommunity: Dict[str, Optional[str]] = {}
twitchCommunityId: Dict[str, str] = {}
twitchCommunityCache: Dict[str, datetime] = {}
displayName: str = bot.config.botnick
isTwitchAdmin: bool = False
isTwitchStaff: bool = False
isGlobalMod: bool = False
emoteset: List[int] = [0]
globalEmotes: Dict[int, str] = {
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
    }
globalEmoteSets: Dict[int, int] = {k: 0 for k, v in globalEmotes.items()}
globalEmotesCache: datetime = datetime.min
globalSessionData: Dict[Any, Any] = {}
globalFfzEmotes: Dict[int, str] = {
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
globalFfzEmotesCache: datetime = datetime.min
globalBttvEmotes: Dict[str, str] = {}
globalBttvEmotesCache: datetime = datetime.min
