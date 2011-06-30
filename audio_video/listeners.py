from models import Video
from processing import make_flv_for, take_snapshot_for, WrongFfmpegFormat
from django.core.mail import send_mail
from django.db.models import signals
from django.conf import settings
from django.conf import settings

def upload_to_s3(filename):
    if settings.DEFAULT_FILE_STORAGE ==\
            "django.core.files.storage.FileSystemStorage":
        return
    from storages.backends.s3boto import S3BotoStorageFile, S3BotoStorage
    import os    
    storage = S3BotoStorage()
    key = storage.bucket.get_key(storage._encode_name(filename))
    if not key:
        key = storage.bucket.new_key(storage._encode_name(filename))
    key.set_contents_from_filename(settings.VIDEOS_TEMP_DIR+filename)
    key.close()

def update(sender, instance, created, **kwargs):
    if not settings.UPLOAD_VIDEOS_TO_S3:
        return
    changed = True
    if created:
        if not instance.flv_file.name:
            instance.flv_file = make_flv_for(instance)
            instance.flv_file._committed = False
            changed = True
            
        try:
            
            from PIL import Image
            new_splash = take_snapshot_for(instance)
            instance.splash_image = new_splash
            changed = True
            upload_to_s3(instance.upload_file.name)
            upload_to_s3(instance.splash_image.name)
            image = Image.open(
                settings.VIDEOS_TEMP_DIR+instance.splash_image.name)
            for thumb in instance.splash_image.field.thumbs:
                thumb_name, thumb_options = thumb
                instance.splash_image.create_and_store_thumb(image,
                                                             thumb_name,
                                                             thumb_options)
    
        except WrongFfmpegFormat:
            from main.models import UserVideo
            UserVideo.objects.filter(video=instance).delete()
            return
            
        if changed:
            if settings.DEFAULT_FILE_STORAGE ==\
                    "django.core.files.storage.FileSystemStorage":
                return

            instance.save()
            upload_to_s3(instance.flv_file.name)
            import os
            os.remove(settings.VIDEOS_TEMP_DIR+instance.upload_file.name)
            os.remove(settings.VIDEOS_TEMP_DIR+instance.flv_file.name)
            os.remove(settings.VIDEOS_TEMP_DIR+instance.splash_image.name)

            if instance.splash_image == "":
                from main.models import UserVideo
                UserVideo.objects.filter(video=instance).delete()
                return
                raise WrongFfmpegFormat
            
signals.post_save.connect(update, sender=Video)
