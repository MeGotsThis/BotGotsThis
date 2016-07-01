from bot import data
from bot.twitchmessage import IrcMessageTagsReadOnly
from bot.data.error import LoginUnsuccessful
from typing import Optional

invalidLogin = [
    'Login unsuccessful',
    'Error logging in',

    # https://discuss.dev.twitch.tv/t/6542
    'Login authentication failed',
    'Improperly formatted auth',
    ]

def parse(tags: IrcMessageTagsReadOnly,
          chat: 'Optional[data.Channel]',
          nick: Optional[str],
          message: Optional[str]) -> None:
    if message in invalidLogin and nick is None and chat is None:
        raise LoginUnsuccessful()
    if (isinstance(tags, IrcMessageTagsReadOnly)
            and isinstance(chat, data.Channel)
            and 'msg-id' in tags):
        msgId = tags['msg-id']
        if msgId in ['msg_duplicate', 'msg_ratelimit']:
            chat.isMod = False
        if msgId in ['msg_banned', 'msg_timedout']:
            chat.isMod = False
            chat.clear()
