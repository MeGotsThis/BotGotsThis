from lib.data import WhisperCommandArgs
from lib.helper.whisper import send
from ..library import broadcaster


async def commandEmpty(args: WhisperCommandArgs) -> bool:
    return broadcaster.empty(args.nick, send(args.nick))
