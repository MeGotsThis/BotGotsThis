from ..library.chat import permission
from ...data import ManageBotArgs, Send
from ...database import DatabaseMain


@permission('owner')
async def manageManager(args: ManageBotArgs) -> bool:
    if len(args.message) < 4:
        return False
    user: str = args.message.lower[3]
    if args.message.lower[2] in ['add', 'insert']:
        return await insert_manager(user, args.database, args.send)
    if args.message.lower[2] in ['del', 'delete', 'rem', 'remove']:
        return await delete_manager(user, args.database, args.send)
    return False


async def insert_manager(user: str,
                         database: DatabaseMain,
                         send: Send) -> bool:
    manager: bool = await database.isBotManager(user)
    if manager:
        send('{user} is already a manager'.format(user=user))
        return True
    successful: bool = await database.addBotManager(user)
    msg: str
    if successful:
        msg = '{user} is now a manager'
    else:
        msg = '{user} could not be added as a manager. Error has occured.'
    send(msg.format(user=user))
    return True


async def delete_manager(user: str,
                         database: DatabaseMain,
                         send: Send) -> bool:
    manager: bool = await database.isBotManager(user)
    if not manager:
        send('{user} is already not a manager'.format(user=user))
        return True
    successful: bool = await database.removeBotManager(user)
    msg: str
    if successful:
        msg = '{user} has been removed as a manager'
    else:
        msg = '{user} could not be removed as a manager. Error has occured.'
    send(msg.format(user=user))
    return True
