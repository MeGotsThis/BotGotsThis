import bot.config
from bot import utils
from typing import Iterable, List, Optional
from ..library.chat import permission
from ...data import ManageBotArgs, Send
from ...database import DatabaseBase


@permission('owner')
def manageManager(args: ManageBotArgs) -> bool:
    if len(args.message) < 4:
        return False
    user = args.message.lower[3]  # type: str
    if args.message.lower[2] in ['add', 'insert']:
        return insert_manager(user, args.database, args.send)
    if args.message.lower[2] in ['del', 'delete', 'rem', 'remove']:
        return delete_manager(user, args.database, args.send)
    return False


def insert_manager(user: str,
                   database: DatabaseBase,
                   send: Send) -> bool:
    if database.isBotManager(user):
        send('{user} is already a manager'.format(user=user))
        return True
    if database.addBotManager(user):
        msg = '{user} is now a manager'
    else:
        msg = '{user} could not be added as a manager. Error has occured.'
    send(msg.format(user=user))
    return True


def delete_manager(user: str,
                   database: DatabaseBase,
                   send: Send) -> bool:
    if not database.isBotManager(user):
        send('{user} is already not a manager'.format(user=user))
        return True
    if database.removeBotManager(user):
        msg = '{user} has been removed as a manager'
    else:
        msg = '{user} could not be removed as a manager. Error has occured.'
    send(msg.format(user=user))
    return True
