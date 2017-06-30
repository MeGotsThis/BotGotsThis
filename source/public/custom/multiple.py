from typing import Dict, List, Optional, Union  # noqa: F401
from ...data import CustomProcessArgs


async def propertyMultipleLines(args: CustomProcessArgs) -> None:
    if not await args.database.getCustomCommandProperty(
            args.broadcaster, args.level, args.command, 'multiple'):
        return

    value: Optional[Union[str, Dict[str, str]]]
    value = await args.database.getCustomCommandProperty(
        args.broadcaster, args.level, args.command, 'delimiter')
    delimiter: str = (value if isinstance(value, str) else '') or '&&'

    msgs: List[str] = args.messages[:]
    args.messages.clear()
    msg: str
    for msg in msgs:
        args.messages.extend(msg.split(delimiter))
