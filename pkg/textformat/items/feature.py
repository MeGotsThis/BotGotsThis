from typing import Mapping, Optional


def features() -> Mapping[str, Optional[str]]:
    if not hasattr(features, 'features'):
        setattr(features, 'features', {
            'textconvert': 'Text Character Conversion',
        })
    return getattr(features, 'features')
