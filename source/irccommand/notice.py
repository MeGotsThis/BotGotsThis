from bot import data
from bot.data.error import LoginUnsuccessful

messageLimit = ('Your message was not sent because you are '
                'sending messages too quickly.')  # type: str
messageIdentical = ('Your message was not sent because it is identical to the '
                    'previous one you sent, less than 30 seconds ago.')  # type: str


def parse(chat: 'data.Channel',
          nick: str,
          message: str) -> None:
    if message == 'Login unsuccessful':
        raise LoginUnsuccessful()
    if message.startswith('You are permanently banned from talking in '):
        chat.isMod = False
        chat.clear()
