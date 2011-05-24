from fields import VideoFileField, AudioFileField, DurationField
from processing import get_video_specs
from widgets import ReadOnlyWidget
import signals
import re
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from flv_reader import FLVReader
import datetime
import os
import subprocess

from django.core.files.storage import FileSystemStorage
fs = FileSystemStorage(location=settings.VIDEOS_TEMP_DIR)
#fs = FileSystemStorage(location=settings.MEDIA_ROOT)
from athumb.fields import ImageWithThumbsField
from athumb.backends.s3boto import S3BotoStorage_AllPublic
PUBLIC_MEDIA_BUCKET = S3BotoStorage_AllPublic(settings.AWS_STORAGE_BUCKET_NAME)

def get_duration_from_video(video):
    duration = video.flv_file._get_metadata()['duration']
    duration_re = re.compile(r'(\d\d):(\d\d):(\d\d).(\d\d)')
    m = duration_re.match(duration)
    value = None
    if m:
        value = datetime.timedelta(
            hours=int(m.group(1)),
            minutes=int(m.group(2)),
            seconds=int(m.group(3)) + int(m.group(4)) / 1000.)
        return value
    return None


# Use django-tagging TagField if available and loaded,
# otherwise substitude a dummy TagField.
#
# Taken from django-photologue <http://code.google.com/p/django-photologue/>
try:
    if not 'tagging' in settings.INSTALLED_APPS: raise ImportError
    from tagging.fields import TagField
    tagfield_help_text = _("separate tags with spaces, put quotes around multiple-word tags.")
except ImportError:
    class TagField(models.CharField):
        def __init__(self, **kwargs):
            default_kwargs = { 'max_length': 255, 'blank': True }
            default_kwargs.update(kwargs)
            super(TagField, self).__init__(**default_kwargs)
        def get_internal_type(self):
            return 'CharField'
    tagfield_help_text = _("django-tagging was not found, tags will be treated as plain text.")

class VideoSize(models.Model):
    """
    Define a video size for video model instances.
    """
    title = models.CharField(_('title'), max_length=40)
    width = models.PositiveIntegerField(_('width'))
    height = models.PositiveIntegerField(_('height'))

    class Meta:
        ordering = ('-width', '-height')
        verbose_name = _('video size')
        verbose_name_plural = _('video sizes')

    def __unicode__(self):
        return u'%s (%dx%d)' % (self.title, self.width, self.height)

    @property
    def as_pair(self):
        return u'%dx%d' % (self.width, self.height)

class Video(models.Model):
    """
    Store a video file and automatically maintain a Flash Video (.flv) version for playback.
    """
    title = models.CharField(_('title'), max_length=120)
    description = models.TextField(_('description'), blank=True)
    size = models.ForeignKey(VideoSize, verbose_name=_('size'))
    upload_file = VideoFileField(_('upload video file'),
                                 upload_to='video/upload/%Y/%m/%d',
                                 storage=fs)
    flv_file = VideoFileField(_('final video file'),
                              upload_to='video/flv/%Y/%m/%d',
                              blank=True,
                              duration_field='duration',
                              width_field='width',
                              height_field='height',
                              read_only=True,
                              storage=fs)
    splash_image = ImageWithThumbsField(
        _('splash image'),
        upload_to='video/splash/%Y/%m/%d',
        blank=True, null=True,
        storage=PUBLIC_MEDIA_BUCKET,
        thumbs=(
        ('90x90', {'size': (90, 90), 'crop':False, 'upscale':False}),
        ('130x100', {'size': (200,150), 'crop':'center', 'upscale':True}),
        ('130x100_crop', {'size': (130,100), 'crop':'center', 'upscale':False}),
        ))
    auto_position = models.CharField(_('capture splash image at'), max_length=12, blank=True,
        help_text=u"To capture a splash image from the video, enter video position in seconds "
                  u"or in hh:mm:ss[.xxx] format. Auto-capture would not occur if this field "
                  u"is empty or if an image file has been selected for upload.")
    date = models.DateTimeField(_('release date'), blank=True, null=True)
    tags = TagField(verbose_name=_('tags'), help_text=tagfield_help_text)
    duration = DurationField(_('duration'), blank=True, null=True)
    width = models.PositiveIntegerField(_('width'), blank=True, null=True)
    height = models.PositiveIntegerField(_('height'), blank=True, null=True)

    class Meta:
        verbose_name = _('video')
        verbose_name_plural = _('videos')

    def __unicode__(self):
        return self.title

    def save(self, **kwargs):
        if not self.id:
            self.date = datetime.datetime.now()
        super(Video, self).save(**kwargs)
        #if hasattr(self, '_metadata'):
        #    del self._metadata

        
    @models.permalink
    def get_absolute_url(self):
        return ('video', [self.id])

    def metadata(self):
        #self.save()
        if not hasattr(self, '_metadata'):
            #self._metadata = get_video_specs(self.flv_file.name)
            self._metadata = self.flv_file._get_metadata()
        #try:
        #    self._metadata = FLVReader(os.path.join(settings.MEDIA_ROOT, self.flv_file.name))
        #except (ValueError, KeyError):
        #    self._metadata = {
        #        'duration': 0,
        #        'width': settings.VIDEO_FLV_SIZE[0],
        #        'height': settings.VIDEO_FLV_SIZE[1],
        #    }
        #self.duration = self._metadata['duration']
        #self.save()
        return self._metadata

    #def size(self):
    #    return filesizeformat(self.video_file.size)

class Audio(models.Model):
    """
    Store an audio file.
    """
    title = models.CharField(_('title'), max_length=40)
    description = models.TextField(_('description'), blank=True)
    file = AudioFileField(_('audio file'), upload_to='audio/%Y/%m/%d', duration_field='duration', bitrate_field='bitrate')
    date = models.DateTimeField(_('release date'), blank=True, null=True)
    tags = TagField(verbose_name=_('tags'), help_text=tagfield_help_text)
    duration = DurationField(_('duration'), blank=True, null=True)
    bitrate = models.IntegerField(_('bitrate'), blank=True, null=True)

    class Meta:
        verbose_name = _('audio file')
        verbose_name_plural = _('audio files')

    def __unicode__(self):
        return self.title

    def save(self, **kwargs):
        if not self.bitrate:
            self.duration = self.file.duration()
            self.bitrate = self.file.bitrate()
        super(Audio, self).save(**kwargs)
#     @property
#     def file_size(self):
#         return self.file.size
# 
#     def _get_metadata(self):
#         if not hasattr(self, '_metadata'):
#             import mutagen
#             file = mutagen.File(self.file.name)
#             details = {
#                 'duration': datetime.timedelta(seconds=file.info.length),
#                 'bitrate': file.info.bitrate,
#             }
#             self._metadata = details
#         return self._metadata

    def metadata(self):
        #self.save()
        if not hasattr(self, '_metadata'):
            #self._metadata = get_video_specs(self.flv_file.name)
            self._metadata = self.file._get_metadata()
        #try:
        #    self._metadata = FLVReader(os.path.join(settings.MEDIA_ROOT, self.flv_file.name))
        #except (ValueError, KeyError):
        #    self._metadata = {
        #        'duration': 0,
        #        'width': settings.VIDEO_FLV_SIZE[0],
        #        'height': settings.VIDEO_FLV_SIZE[1],
        #    }
        #self.duration = self._metadata['duration']
        #self.save()
        return self._metadata
