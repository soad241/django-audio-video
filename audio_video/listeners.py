from models import Video
from processing import make_flv_for, take_snapshot_for, WrongFfmpegFormat
from django.core.mail import send_mail
from django.db.models import signals
from django.conf import settings

def update(sender, instance, **kwargs):
    changed = False

    if not instance.flv_file.name:
        instance.flv_file = make_flv_for(instance)
        instance.flv_file._committed = False
        changed = True

    if instance.auto_position:
        try:
            new_splash = take_snapshot_for(instance)
        except WrongFfmpegFormat:
            from main.models import UserVideo
            UserVideo.objects.filter(video=instance).delete()
            return
        if instance.splash_image != new_splash:
            instance.splash_image = new_splash
            changed = True

    if changed:
        instance.save()

signals.post_save.connect(update, sender=Video)
