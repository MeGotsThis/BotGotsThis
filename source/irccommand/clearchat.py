from bot import config, data


def parse(chat: 'data.Channel',
          nick: str):
    if nick == config.botnick:
        chat.isMod = False
        chat.socket.messaging.clearChat(chat)
