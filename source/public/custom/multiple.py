from typing import Dict, List, Optional, Union
from ...data import CustomProcessArgs


async def propertyMultipleLines(args: CustomProcessArgs) -> None:
    if not args.database.getCustomCommandProperty(
            args.broadcaster, args.level, args.command, 'multiple'):
        return

    value: Optional[Union[str, Dict[str, str]]]
    value = args.database.getCustomCommandProperty(
        args.broadcaster, args.level, args.command, 'delimiter'
        )
    delimiter: str = (value if isinstance(value, str) else '') or '&&'
    
    msgs: List[str] = args.messages[:]
    args.messages.clear()
    msg: str
    for msg in msgs:
        args.messages.extend(msg.split(delimiter))
