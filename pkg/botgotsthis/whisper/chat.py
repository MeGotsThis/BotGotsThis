from lib.data import WhisperCommandArgs
from lib.helper.whisper import send
from ..library import chat


async def commandEmpty(args: WhisperCommandArgs) -> bool:
    return chat.empty(args.nick, send(args.nick))
