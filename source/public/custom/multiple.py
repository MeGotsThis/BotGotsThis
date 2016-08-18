from typing import List
from ...data import CustomProcessArgs


def propertyMultipleLines(args: CustomProcessArgs) -> None:
    if not args.database.getCustomCommandProperty(
            args.broadcaster, args.level, args.command, 'multiple'):
        return

    delimiter = args.database.getCustomCommandProperty(  # type: ignore --
        args.broadcaster, args.level, args.command, 'delimiter') or '&&'  # type: str
    
    msgs = args.messages[:]  # type: List[str]
    args.messages.clear()
    for msg in msgs:  # --type: str
        args.messages.extend(msg.split(delimiter))
