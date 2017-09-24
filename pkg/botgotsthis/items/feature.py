from typing import Mapping, Optional


def features() -> Mapping[str, Optional[str]]:
    if not hasattr(features, 'features'):
        setattr(features, 'features', {
            'textconvert': 'Text Character Conversion',
            'nocustom': 'Disable Custom Commands',
            'nourlredirect': 'Ban URL Redirect (user has no follows)',
            'gamestatusbroadcaster': '!game and !status only for broadcaster',
        })
    return getattr(features, 'features')
