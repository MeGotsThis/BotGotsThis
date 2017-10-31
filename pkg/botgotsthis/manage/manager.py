from lib.cache import CacheStore
from lib.data import ManageBotArgs, Send
from lib.helper.chat import permission


@permission('owner')
async def manageManager(args: ManageBotArgs) -> bool:
    if len(args.message) < 4:
        return False
    user: str = args.message.lower[3]
    if args.message.lower[2] in ['add', 'insert']:
        return await insert_manager(user, args.data, args.send)
    if args.message.lower[2] in ['del', 'delete', 'rem', 'remove']:
        return await delete_manager(user, args.data, args.send)
    return False


async def insert_manager(user: str,
                         data: CacheStore,
                         send: Send) -> bool:
    manager: bool = await data.isBotManager(user)
    if manager:
        send(f'{user} is already a manager')
        return True
    successful: bool = await data.addBotManager(user)
    if successful:
        send(f'{user} is now a manager')
    else:
        send(f'{user} could not be added as a manager. Error has occured.')
    return True


async def delete_manager(user: str,
                         data: CacheStore,
                         send: Send) -> bool:
    manager: bool = await data.isBotManager(user)
    if not manager:
        send(f'{user} is already not a manager')
        return True
    successful: bool = await data.removeBotManager(user)
    if successful:
        send(f'{user} has been removed as a manager')
    else:
        send(f'{user} could not be removed as a manager. Error has occured.')
    return True
