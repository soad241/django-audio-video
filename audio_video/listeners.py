from models import Video
from processing import make_flv_for, take_snapshot_for, WrongFfmpegFormat
from django.core.mail import send_mail
from django.db.models import signals
from django.conf import settings
from django.conf import settings

def upload_to_s3(filename):
    from storages.backends.s3boto import S3BotoStorageFile, S3BotoStorage
    import os    
    storage = S3BotoStorage()
    fn = S3BotoStorageFile(filename, 'w', storage)
    key = storage.bucket.get_key(storage._encode_name(filename))
    if not key:
        key = storage.bucket.new_key(storage._encode_name(filename))
    key.set_contents_from_filename(settings.VIDEOS_TEMP_DIR+filename)
    key.close()

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
            upload_to_s3(instance.upload_file.name)
            upload_to_s3(instance.flv_file.name)
            upload_to_s3(instance.splash_image.name)
            from easy_thumbnails.files import get_thumbnailer
            from main.templatetags.main_tags import main_get_video_size_width, \
                 main_get_video_size_height
            video = Video.objects.get(pk=instance.pk)
            w = main_get_video_size_width(video)
            h = main_get_video_size_height(video)
            thumbnail_options = dict(size=(w, h), upscale=True, crop="smart")
            thumb = get_thumbnailer(video.splash_image).get_thumbnail(
                thumbnail_options)
            #upload_to_s3(thumb.name)
            import os
            os.remove(settings.VIDEOS_TEMP_DIR+instance.upload_file.name)
            os.remove(settings.VIDEOS_TEMP_DIR+instance.flv_file.name)
            os.remove(settings.VIDEOS_TEMP_DIR+instance.splash_image.name)
            
signals.post_save.connect(update, sender=Video)
