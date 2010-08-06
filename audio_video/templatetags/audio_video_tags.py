from audio_video import settings
from audio_video.models import Audio, Video
#from media_anywhere.thumbnail import resize_image

from django import template
from django.db import models
from django.template import Context, loader, Variable
from django.utils.safestring import mark_safe

register = template.Library()

def _render_audio(instance, params):
    t = template.loader.get_template('audio_video/audio/%s/include.html' % settings.AUDIO_PLAYER)
    ctx = Context({
        'audio': instance,
        'media_url': settings.MEDIA_URL,
    })
    return t.render(ctx)

def _render_video(instance, params):
    t = template.loader.get_template('audio_video/video/%s/include.html' % settings.VIDEO_PLAYER)
    try:
        metadata = instance.metadata()
    except:
        t = template.loader.get_template('audio_video/video/error.html')
        ctx = Context({})
        return t.render(ctx)
    ctx = Context({
        'video': instance,
        'metadata': metadata,
        'media_url': settings.MEDIA_URL,
        'provider': settings.VIDEO_PROVIDER,
    })
    return t.render(ctx)

class PlayerNode(template.Node):

    def __init__(self, instance, params):
        self.instance, self.params = template.Variable(instance), params

    def render(self, context):
        instance = self.instance.resolve(context)
        if instance.__class__ == Video:
            return _render_video(instance, self.params)
        elif instance.__class__ == Audio:
            return _render_audio(instance, self.params)
        else:
            raise Exception, "'render_player' tag received an unsupported model instance (%s)" \
                % instance.__class__

@register.tag
def render_player(parser, token):
    bits = token.split_contents()[1:]
    try:
        instance = bits[0]
    except IndexError:
        raise template.TemplateSyntaxError, "'render_player' tag requires at least one argument"
    return PlayerNode(instance, bits[1:])
