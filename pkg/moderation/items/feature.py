from typing import Mapping, Optional


def features() -> Mapping[str, Optional[str]]:
    if not hasattr(features, 'features'):
        setattr(features, 'features', {
            'nourlredirect': 'Ban URL Redirect (user has no follows)',
        })
    return getattr(features, 'features')
