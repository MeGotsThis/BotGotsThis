from .public import whisper as publicList
from collections import ChainMap
from source.data.argument import WhisperCommandArgs
from typing import Callable, Mapping, Optional
try:
    from .private import whisper as privateList
except ImportError:
    from .private.default import whisper as privateList  # type: ignore

commands = ChainMap(privateList.commands, publicList.commands)  # type: Mapping[str, Optional[Callable[[WhisperCommandArgs], bool]]]
