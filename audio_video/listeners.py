from models import Video
from processing import make_flv_for, take_snapshot_for, WrongFfmpegFormat
from django.core.mail import send_mail
from django.db.models import signals
from django.conf import settings

def update(sender, instance, created, **kwargs):
    changed = False
    if created:
        if not instance.flv_file.name:
            instance.flv_file = make_flv_for(instance)
            instance.flv_file._committed = False
            changed = True

        try:
            new_splash = take_snapshot_for(instance)
            instance.splash_image = new_splash
            changed = True
        except WrongFfmpegFormat:
            from main.models import UserVideo
            UserVideo.objects.filter(video=instance).delete()
            return
            
        if changed:
            instance.save()
            from easy_thumbnails.files import get_thumbnailer
            from main.templatetags.main_tags import main_get_video_size_width, \
                 main_get_video_size_height
            video = Video.objects.get(pk=instance.pk)
            w = main_get_video_size_width(video)
            h = main_get_video_size_height(video)
            thumbnail_options = dict(size=(w, h), upscale=True, crop="smart")
            thumb = get_thumbnailer(video.splash_image).get_thumbnail(
                thumbnail_options)
            
signals.post_save.connect(update, sender=Video)
