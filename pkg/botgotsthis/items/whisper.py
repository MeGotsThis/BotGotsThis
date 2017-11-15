from lib import data
from ..whisper import chat, owner, reload
from typing import Mapping, Optional


def commands() -> Mapping[str, Optional[data.WhisperCommand]]:
    if not hasattr(commands, 'commands'):
        setattr(commands, 'commands', {
            '!hello': owner.commandHello,
            '!exit': owner.commandExit,
            '!say': owner.commandSay,
            '!join': owner.commandJoin,
            '!part': owner.commandPart,
            '!emptychat': owner.commandEmpty,
            '!emptyall': owner.commandEmptyAll,
            '!managebot': owner.commandManageBot,
            '!reload': reload.commandReload,
            '!reloadcommands': reload.commandReloadCommands,
            '!reloadconfig': reload.commandReloadConfig,
            '!refreshcache': reload.commandRefreshCache,
            '!empty': chat.commandEmpty,
            })
    return getattr(commands, 'commands')


def commandsStartWith() -> Mapping[str, Optional[data.WhisperCommand]]:
    return {}
