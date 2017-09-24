from typing import Mapping, Optional


def features() -> Mapping[str, Optional[str]]:
    if not hasattr(features, 'features'):
        setattr(features, 'features', {
            'modpyramid': 'Mods Using !pyramid',
            'modwall': 'Mods Using !wall',
        })
    return getattr(features, 'features')
