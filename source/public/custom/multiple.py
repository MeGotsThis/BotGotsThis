from typing import Dict, List, Optional, Union
from ...data import CustomProcessArgs


def propertyMultipleLines(args: CustomProcessArgs) -> None:
    if not args.database.getCustomCommandProperty(
            args.broadcaster, args.level, args.command, 'multiple'):
        return

    value = args.database.getCustomCommandProperty(
        args.broadcaster, args.level, args.command, 'delimiter'
        )  # type: Optional[Union[str, Dict[str, str]]]
    delimiter = (value if isinstance(value, str) else '') or '&&'  # type: str
    
    msgs = args.messages[:]  # type: List[str]
    args.messages.clear()
    for msg in msgs:  # type: str
        args.messages.extend(msg.split(delimiter))
