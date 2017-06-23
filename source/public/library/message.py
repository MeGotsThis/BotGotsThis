import bot
from collections import deque
from typing import Generator, Iterable, Optional


def messagesFromItems(items:Iterable[str],
                      prepend:Optional[str]=None) -> Generator[str, None, None]:
    prepend = prepend or ''
    limit: int = bot.config.messageLimit - len(prepend)
    queue: deque = deque(items)
    itemsMsg: deque= deque()
    length: int = 0
    while queue:
        item: str = queue.popleft()
        itemsMsg.append(item)
        if length:
            length += 2
        length += len(item)
        if length >= limit:
            if len(itemsMsg) > 1:
                itemsMsg.pop()
                yield prepend + ', '.join(itemsMsg)
                itemsMsg.clear()
                itemsMsg.append(item)
                length = len(item)
            else:
                yield prepend + ', '.join(itemsMsg)
                itemsMsg.clear()
                length = 0
    if itemsMsg:
        yield prepend + ', '.join(itemsMsg)
