from contextlib import suppress
from typing import List, Optional  # noqa: F401
from ..library.chat import min_args, permission
from ...data import ChatCommandArgs
from ...database import AutoRepeatList  # noqa: F401


@permission('broadcaster')
async def commandAutoRepeat(args: ChatCommandArgs) -> bool:
    """
    !autorepeat 1 MONEY MONEY
    !autorepeat 0
    !autorepeat off
    """

    count: Optional[int] = None
    return await process_auto_repeat(args, count)


@permission('broadcaster')
async def commandAutoRepeatCount(args: ChatCommandArgs) -> bool:
    """
    !autorepeat-20 0.5 MONEY MONEY
    !autorepeat-20 0
    !autorepeat-20 off
    """

    count: Optional[int] = 10
    with suppress(ValueError, IndexError):
        count = int(args.message.command.split('autorepeat-')[1])
    return await process_auto_repeat(args, count)


@min_args(2)
async def process_auto_repeat(args: ChatCommandArgs,
                              count: Optional[int]) -> bool:
    name: str = ''
    minutesDuration: float = 0
    message: Optional[str] = None

    secondArg: str = ''
    if args.message.lower[1].startswith('name='):
        name = args.message.lower[1].split('name=', 1)[1]
        if len(args.message) >= 3:
            secondArg = args.message.lower[2]
            message = args.message[3:] or None
    else:
        secondArg = args.message.lower[1]
        message = args.message[2:] or None

    if secondArg == 'list':
        repeats: List[AutoRepeatList]
        repeats = [repeat async for repeat
                   in args.database.listAutoRepeat(args.chat.channel)]
        if not repeats:
            args.chat.send('No Active Auto Repeats')
        else:
            args.chat.send('Active Auto Repeats:')
        repeat: AutoRepeatList
        for repeat in repeats:
            name = repeat.name if repeat.name else '<default>'
            args.chat.send(
                'Name: {name}, Duration: {duration} minutes, '
                'Message: {message}'.format(name=name,
                                            duration=repeat.duration,
                                            message=repeat.message))
        return True
    elif secondArg == 'clear':
        await args.database.clearAutoRepeat(args.chat.channel)
        return True
    elif secondArg == 'off':
        pass
    else:
        try:
            minutesDuration = float(secondArg)
        except ValueError:
            return False

    if minutesDuration <= 0 or count == 0 or not message:
        await args.database.removeAutoRepeat(args.chat.channel, name)
        return True

    await args.database.setAutoRepeat(args.chat.channel, name, message, count,
                                      minutesDuration)
    return True
