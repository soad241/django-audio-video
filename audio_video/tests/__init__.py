# coding: utf-8

r"""
>>> from django.test.client import Client
>>> from django.template import Template, Context
>>> from audio_video.models import *

>>> a = Audio.objects.create(title='My First Song', file='audio/wave.mp3')
>>> a
<Audio: My First Song>

>>> a.file
<AudioFieldFile: audio/wave.mp3>

>>> a.file.duration
datetime.timedelta(0, 1, 567347)

>>> a.file.bitrate
128000








###
### define rendering helper method
###

>>> def _render(ctx={}):
...     return t.render(Context(ctx))
...


"""
