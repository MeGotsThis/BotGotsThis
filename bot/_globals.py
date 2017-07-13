from datetime import datetime

from typing import Any, Dict, Optional, List  # noqa: F401

from . import data  # noqa: F401
from .coroutine import connection  # noqa: F401


class BotGlobals:
    def __init__(self):
        self.running: bool = True

        self.groupChannel: 'data.Channel' = None

        self.clusters: Dict[str, 'connection.ConnectionHandler'] = {
            'aws': None,
        }
        self.whisperCluster: str = 'aws'

        self.channels: Dict[str, 'data.Channel'] = {}
        self.twitchId: Dict[str, Optional[str]] = {}
        self.twitchIdName: Dict[str, str] = {}
        self.twitchIdCache: Dict[str, datetime] = {}
        self.twitchCommunity: Dict[str, Optional[str]] = {}
        self.twitchCommunityId: Dict[str, str] = {}
        self.twitchCommunityCache: Dict[str, datetime] = {}
        self.displayName: str = ''
        self.isTwitchAdmin: bool = False
        self.isTwitchStaff: bool = False
        self.isGlobalMod: bool = False
        self.emoteset: List[int] = [0]
        self.globalEmotes: Dict[int, str] = {
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
        self.globalEmoteSets: Dict[int, int] = {k: 0 for k, v in
                                                self.globalEmotes.items()}
        self.globalEmotesCache: datetime = datetime.min
        self.globalSessionData: Dict[Any, Any] = {}
        self.globalFfzEmotes: Dict[int, str] = {
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
        self.globalFfzEmotesCache: datetime = datetime.min
        self.globalBttvEmotes: Dict[str, str] = {}
        self.globalBttvEmotesCache: datetime = datetime.min
