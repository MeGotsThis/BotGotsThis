from lib.data import ChatCommandArgs
from lib.helper.chat import min_args, permission, send
from ..library import chat


@permission('moderator')
@min_args(2)
async def commandPermit(args: ChatCommandArgs) -> bool:
    mod: str = args.nick
    user: str = args.message.lower[1]
    channel: str = args.chat.channel
    permitted: bool
    permitted = await args.data.isPermittedUser(args.chat.channel, user)
    msg: str
    successful: bool
    if permitted:
        successful = await args.data.removePermittedUser(
            args.chat.channel, user, args.nick)
        if successful:
            msg = f'{mod} -> {user} is now unpermitted in {channel}'
        else:
            msg = f'{mod} -> Error'
    else:
        successful = await args.data.addPermittedUser(
            args.chat.channel, user, args.nick)
        if successful:
            msg = f'{mod} -> {user} is now unpermitted in {channel}'
        else:
            msg = f'{mod} -> Error'
    args.chat.send(msg)
    return True


@permission('broadcaster')
async def commandEmpty(args: ChatCommandArgs) -> bool:
    return chat.empty(args.chat.channel, send(args.chat))


@permission('broadcaster')
async def commandSetTimeoutLevel(args: ChatCommandArgs) -> bool:
    await chat.set_timeout_level(args.data, args.chat.channel, send(args.chat),
                                 args.message)
    return True
