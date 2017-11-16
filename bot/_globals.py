import aioodbc  # noqa: F401
import aioredis  # noqa: F401

from typing import Any, Dict, Tuple  # noqa: F401

from . import data  # noqa: F401
from .coroutine import connection  # noqa: F401


class BotGlobals:
    def __init__(self) -> None:
        self.running: bool = True

        self.groupChannel: 'data.Channel' = None

        self.cluster: 'connection.ConnectionHandler' = None
        self.whisperCluster: str = 'aws'

        self.channels: Dict[str, 'data.Channel'] = {}
        self.displayName: str = ''
        self.isTwitchAdmin: bool = False
        self.isTwitchStaff: bool = False
        self.isGlobalMod: bool = False
        self.globalSessionData: Dict[Any, Any] = {}

        self.pkgs: Tuple[str, ...] = tuple()
        self.connectionPools: Dict[str, aioodbc.Pool] = {}

        self.redisPool: aioredis.ConnectionsPool
