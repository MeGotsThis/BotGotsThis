from source.data.argument import WhisperCommandArgs
from typing import Callable, Mapping, Optional

commands = {}  # type: Mapping[str, Optional[Callable[[WhisperCommandArgs], bool]]]
