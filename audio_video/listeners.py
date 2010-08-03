from models import Video
from processing import make_flv_for, take_snapshot_for

from django.db.models import signals

def update(sender, instance, **kwargs):
    changed = False

    if not instance.flv_file.name:
        instance.flv_file = make_flv_for(instance)
        instance.flv_file._committed = False
        changed = True

    if instance.auto_position:
        new_splash = take_snapshot_for(instance)
        if instance.splash_image != new_splash:
            instance.splash_image = new_splash
            changed = True

    if changed:
        instance.save()

signals.post_save.connect(update, sender=Video)
