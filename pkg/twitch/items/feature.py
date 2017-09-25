from typing import Mapping, Optional


def features() -> Mapping[str, Optional[str]]:
    if not hasattr(features, 'features'):
        setattr(features, 'features', {
            'gamestatusbroadcaster': '!game and !status only for broadcaster',
        })
    return getattr(features, 'features')
