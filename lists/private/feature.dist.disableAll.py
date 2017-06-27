from typing import Mapping, Optional


def features() -> Mapping[str, Optional[str]]:
    if not hasattr(features, 'features'):
        setattr(features, 'features', {
            'textconvert': None,
            'modpyramid': None,
            'modwall': None,
            'nocustom': None,
            'nourlredirect': None,
            'gamestatusbroadcaster': None,
            })
    return getattr(features, 'features')
