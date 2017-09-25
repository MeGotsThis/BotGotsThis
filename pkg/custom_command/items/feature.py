from typing import Mapping, Optional


def features() -> Mapping[str, Optional[str]]:
    if not hasattr(features, 'features'):
        setattr(features, 'features', {
            'nocustom': 'Disable Custom Commands',
        })
    return getattr(features, 'features')
