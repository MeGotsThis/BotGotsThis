from typing import Mapping, Optional


def features() -> Mapping[str, Optional[str]]:
    if not hasattr(features, 'features'):
        setattr(features, 'features', {
            'helixfossil': 'Ask Helix Fossil',
            'roll.exe': '!roll exe',
            'bingo': 'Bingo Card',
            'roll.emote': '!roll emotes',
            'pokedex': 'Pokedex',
            'noroll': 'Disable !roll',
            'autopurge': 'Auto Purge',
            'autobanword': 'Auto Ban Word',
            'nosrlrace': 'Disable !srlrace',
            'winnerbroadcaster': '!winner only for broadcaster',
            'modstrawpoll': '!strawpoll for mods',
            'noasciiart': 'No Large ASCII Art',
            'nolinks': 'No URLs/Links',
            'annoyinglinks': 'No Annoying URLs/Links',
            'emotespam': 'No Emote Spam',
            'quotes': 'Quotes',
            'countdown': 'Countdown',
            'modtree': 'Mod !tree'
            })
    return getattr(features, 'features')
