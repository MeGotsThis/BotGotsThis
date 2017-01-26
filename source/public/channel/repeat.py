from contextlib import suppress
from typing import List, Optional
from ..library.chat import min_args, permission
from ...data import ChatCommandArgs
from ...database import AutoRepeatList


@permission('broadcaster')
def commandAutoRepeat(args: ChatCommandArgs) -> bool:
    """
    !autorepeat 1 MONEY MONEY
    !autorepeat 0
    !autorepeat off
    """
    
    count = None  # type: Optional[int]
    return process_auto_repeat(args, count)


@permission('broadcaster')
def commandAutoRepeatCount(args: ChatCommandArgs) -> bool:
    """
    !autorepeat-20 0.5 MONEY MONEY 
    !autorepeat-20 0
    !autorepeat-20 off
    """
    
    count = 10  # type: Optional[int]
    with suppress(ValueError, IndexError):
        count = int(args.message.command.split('autorepeat-')[1])
    return process_auto_repeat(args, count)


@min_args(2)
def process_auto_repeat(args: ChatCommandArgs,
                        count: Optional[int]) -> bool:
    name = ''  # type: str
    minutesDuration = 0  # type: float
    message = None  # type: Optional[str]

    secondArg = ''  # type: str
    if args.message.lower[1].startswith('name='):
        name = args.message.lower[1].split('name=', 1)[1]
        if len(args.message) >= 3:
            secondArg = args.message.lower[2]
            message = args.message[3:] or None
    else:
        secondArg = args.message.lower[1]
        message = args.message[2:] or None

    if secondArg == 'list':
        repeats = list(args.database.listAutoRepeat(args.chat.channel)
                       )  # type: List[AutoRepeatList]
        if not repeats:
            args.chat.send('No Active Auto Repeats')
        else:
            args.chat.send('Active Auto Repeats:')
        for repeat in repeats:  # type: AutoRepeatList
            name = repeat.name if repeat.name else '<default>'
            args.chat.send(
                'Name: {name}, Duration: {duration} minutes, '
                'Message: {message}'.format(name=name,
                                            duration=repeat.duration,
                                            message=repeat.message))
        return True
    elif secondArg == 'clear':
        args.database.clearAutoRepeat(args.chat.channel)
        return True
    elif secondArg == 'off':
        pass
    else:
        try:
            minutesDuration = float(secondArg)
        except ValueError:
            return False

    if minutesDuration <= 0 or count == 0 or not message:
        args.database.removeAutoRepeat(args.chat.channel, name)
        return True

    args.database.setAutoRepeat(args.chat.channel, name, message, count,
                                minutesDuration)
    return True
