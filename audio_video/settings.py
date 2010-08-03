from django.conf import settings

import sys

module = sys.modules[__name__]
for attr in dir(settings):
    if attr == attr.upper():
        setattr(module, attr, getattr(settings, attr))

_prefix = 'AV_'

VIDEO_PLAYER = getattr(settings, _prefix + 'VIDEO_PLAYER', 'flowplayer')
AUDIO_PLAYER = getattr(settings, _prefix + 'AUDIO_PLAYER', 'mp3_player')

VIDEO_SIZE = getattr(settings, _prefix + 'VIDEO_SIZE', (320, 240))
VIDEO_PROVIDER = getattr(settings, _prefix + 'VIDEO_PROVIDER', 'http')
