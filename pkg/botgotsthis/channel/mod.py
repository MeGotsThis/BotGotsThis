from lib.data import ChatCommandArgs
from lib.helper.chat import min_args, permission


@permission('moderator')
@min_args(2)
async def commandPermit(args: ChatCommandArgs) -> bool:
    mod: str = args.nick
    user: str = args.message.lower[1]
    channel: str = args.chat.channel
    permitted: bool
    permitted = await args.database.isPermittedUser(args.chat.channel, user)
    msg: str
    successful: bool
    if permitted:
        successful = await args.database.removePermittedUser(
            args.chat.channel, user, args.nick)
        if successful:
            msg = f'{mod} -> {user} is now unpermitted in {channel}'
        else:
            msg = f'{mod} -> Error'
    else:
        successful = await args.database.addPermittedUser(
            args.chat.channel, user, args.nick)
        if successful:
            msg = f'{mod} -> {user} is now unpermitted in {channel}'
        else:
            msg = f'{mod} -> Error'
    args.chat.send(msg)
    return True
