from bot import config
from collections import deque


def messagesFromItems(items, prepend=None):
    limit = config.messageLimit - len(prepend)
    queue = deque(items)
    itemsMsg = deque()
    length = 0
    while queue:
        item = queue.popleft()
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
