from typing import cast

import bot
from ._auto_join import AutoJoinMixin
from ._auto_repeat import AutoRepeatMixin
from ._banned_channels import BannedChannelsMixin
from ._bot_managers import BotManagersMixin
from ._base import Database
from ._chat_properties import ChatPropertiesMixin
from ._custom_commands import CustomCommandsMixin
from ._features import FeaturesMixin
from ._game_abbreviations import GameAbbreviationsMixin
from ._permitted_users import PermittedUsersMixin


class DatabaseMain(AutoJoinMixin, GameAbbreviationsMixin, CustomCommandsMixin,
                   FeaturesMixin, BannedChannelsMixin, ChatPropertiesMixin,
                   PermittedUsersMixin, BotManagersMixin, AutoRepeatMixin,
                   Database):
    async def __aenter__(self) -> 'DatabaseMain':
        return cast(DatabaseMain, await super().__aenter__())

    @staticmethod
    def acquire() -> 'DatabaseMain':
        return DatabaseMain(bot.globals.connectionPools['main'])
