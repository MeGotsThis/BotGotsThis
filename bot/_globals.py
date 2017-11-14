import aioodbc  # noqa: F401
import aioredis  # noqa: F401

from datetime import datetime

from typing import Any, Dict, Optional, List, Tuple  # noqa: F401

from . import data  # noqa: F401
from .coroutine import connection  # noqa: F401


class BotGlobals:
    def __init__(self) -> None:
        self.running: bool = True

        self.groupChannel: 'data.Channel' = None

        self.clusters: Dict[str, 'connection.ConnectionHandler'] = {
            'aws': None,
        }
        self.whisperCluster: str = 'aws'

        self.channels: Dict[str, 'data.Channel'] = {}
        self.displayName: str = ''
        self.isTwitchAdmin: bool = False
        self.isTwitchStaff: bool = False
        self.isGlobalMod: bool = False
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

        self.pkgs: Tuple[str, ...] = tuple()
        self.connectionPools: Dict[str, aioodbc.Pool] = {}

        self.redisPool: aioredis.ConnectionsPool
