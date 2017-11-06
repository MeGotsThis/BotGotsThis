from lib.data import ChatCommandArgs
from lib.helper.chat import min_args, permission, ownerChannel, send
from lib.helper.chat import sendPriority
from ..library import channel, exit, managebot


@ownerChannel
@permission('owner')
async def commandExit(args: ChatCommandArgs) -> bool:
    return await exit.exit(sendPriority(args.chat, 0))


@min_args(3)
@ownerChannel
@permission('owner')
async def commandSay(args: ChatCommandArgs) -> bool:
    return await channel.say(args.nick, args.message.lower[1],
                             args.message[2:])


@min_args(2)
@ownerChannel
@permission('admin')
async def commandJoin(args: ChatCommandArgs) -> bool:
    return await channel.join(args.message.lower[1], send(args.chat))


@min_args(2)
@ownerChannel
@permission('admin')
async def commandPart(args: ChatCommandArgs) -> bool:
    return channel.part(args.message.lower[1], send(args.chat))


@ownerChannel
@permission('admin')
async def commandEmptyAll(args: ChatCommandArgs) -> bool:
    return channel.empty_all(send(args.chat))


@min_args(2)
@ownerChannel
@permission('admin')
async def commandEmpty(args: ChatCommandArgs) -> bool:
    return channel.empty(args.message.lower[1], send(args.chat))


@min_args(2)
@ownerChannel
@permission('manager')
async def commandManageBot(args: ChatCommandArgs) -> bool:
    return await managebot.manage_bot(
        args.data, args.database, args.permissions, send(args.chat),
        args.nick, args.message)
