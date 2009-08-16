from widgets import DurationInput, ReadOnlyWidget
from processing import get_video_specs, MetadataError
import settings

from django.db import models, connection
from django.db.models.fields.files import FieldFile, FileField
from django import forms

from flv_reader import FLVReader

import datetime
import os
import tempfile
from cStringIO import StringIO
import re

class ReadOnlyField(forms.Field):
    """
    A generic read-only form field.
    """
    widget = ReadOnlyWidget

    def __init__(self, **kwargs):
        super(ReadOnlyField, self).__init__(**kwargs)
        self.widget.initial = kwargs.get('initial', None)

    def clean(self, value):
        return self.widget.initial

class ReadOnlyFileField(ReadOnlyField):
    def __init__(self, *args, **kwargs):
        self.max_length = kwargs.pop('max_length', None)
        super(ReadOnlyFileField, self).__init__(*args, **kwargs)

#-----------------------------------------------
# Provide time duration storage for media files
#-----------------------------------------------

duration_re = re.compile(r'(\d\d):(\d\d):(\d\d).(\d\d)')

class DurationProxy(object):
    def __init__(self, field):
        self.field_name = field.name

    def __get__(self, instance, type=None):
        if instance is None:
            raise AttributeError, "%s can only be accessed from %s instances." % (self.field_name, owner.__name__)
        if self.field_name not in instance.__dict__:
            return None
        return instance.__dict__[self.field_name]

    def __set__(self, obj, value):
        if not isinstance(value, datetime.timedelta) and not value in (None, ''):
            try:
                value = datetime.timedelta(seconds=float(value) / 1000000.)
            except (ValueError, TypeError):
                m = duration_re.match(value)
                if m:
                    value = datetime.timedelta(hours=int(m.group(1)),
                                               minutes=int(m.group(2)),
                                               seconds=int(m.group(3)) + int(m.group(4)) / 1000.)
        obj.__dict__[self.field_name] = value

class DurationField(models.Field):
    """
     A model field storing time durations in seconds, with microsecond precision.
    """
    def __init__(self, *args, **kwargs):
        super(DurationField, self).__init__(*args, **kwargs)
        self.max_digits, self.decimal_places = 20, 6

    def contribute_to_class(self, cls, name):
        super(DurationField, self).contribute_to_class(cls, name)
        setattr(cls, name, DurationProxy(self))

    def get_internal_type(self):
        return "DecimalField"

    def to_python(self, value):
        """Returns value represented as a timedelta.
        """
        if value is None:
            return value
        if isinstance(value, datetime.timedelta):
            return value
        m = duration_re.search(value)
        if m:
            value = datetime.timedelta(hours=int(m.group(1)),
                                       minutes=int(m.group(2)),
                                       seconds=int(m.group(3)) + int(m.group(4)) / 1000.)
            return value

    def create(self, value):
        return datetime.timedelta(seconds=float(value) or 0)

    def flatten_data(self, follow, obj=None):
        val = self._get_val_from_obj(obj)
        if val is None or val is '':
            return ''
        return { self.attname: self.get_db_prep_save(val) }

    def get_db_prep_save(self, value):
        # Casts value into a Decimal format expected by the backend
        value = self.to_python(value)
        if value:
            t = value.seconds * 1000000 + value.microseconds
        else:
            t = 0
        return connection.ops.value_to_db_decimal(t, self.max_digits, self.decimal_places)

    def formfield(self, **kwargs):
        defaults = { 'form_class': ReadOnlyField, 'widget': DurationInput }
        defaults.update(kwargs)
        return super(DurationField, self).formfield(**defaults)

#---------------------------------------
# Model support for storing video files
#---------------------------------------

class VideoFieldFile(FieldFile):
    """
    A video file stored in a model field.
    """
    @property
    def duration(self):
        try:
            return self._get_metadata()['duration']
        except MetadataError:
            return None

    @property
    def width(self):
        try:
            return self._get_metadata()['width']
        except MetadataError:
            return None

    @property
    def height(self):
        try:
            return self._get_metadata()['height']
        except MetadataError:
            return None

    @property
    def _metadata(self):
        if not hasattr(self, '_metadata_cache'):
            self._metadata_cache = get_video_specs(name=self.name)
        return self._metadata_cache

    def _get_metadata(self, file=None):
        if not hasattr(self, '_metadata_cache'):
            if not self:
                raise MetadataError
            metadata = get_video_specs(name=self.name)
            self._metadata_cache = metadata
        return self._metadata_cache

    def save(self, name, content, save=True):
        # Clear stale metadata, if it exists
        if hasattr(self, '_metadata_cache'):
            del self._metadata_cache

        # if field contains in-memory unsaved data, extract metadata from it
        #if not self._committed:
        #    print >>sys.stderr, '##### in memory'
        #    self._get_metadata(file=content)
        #else:
        #    print >>sys.stderr, '##### disk file %s' % self.name
        #    self._get_metadata()

        # Update duration and size fields, if needed
        if self.field.duration_field:
            setattr(self.instance, self.field.duration_field, self.duration)
        if self.field.width_field:
            setattr(self.instance, self.field.width_field, self.width)
        if self.field.height_field:
            setattr(self.instance, self.field.height_field, self.height)

        super(VideoFieldFile, self).save(name, content, save)
    save.alters_data = True

    def delete(self, save=True):
        if hasattr(self, '_metadata_cache'):
            del self._metadata_cache
        super(VideoFieldFile, self).delete(save)
    delete.alters_data = True

class VideoFileField(models.FileField):
    """
    A custom file field which can provide information about stored content.
    """
    attr_class = VideoFieldFile

    def __init__(self, verbose_name=None, name=None, duration_field=None, width_field=None, height_field=None,
                 read_only=False, **kwargs):
        self.duration_field = duration_field
        self.width_field = width_field
        self.height_field = height_field
        self.read_only = read_only
        super(VideoFileField, self).__init__(verbose_name, name, **kwargs)

    def pre_save(self, model_instance, add):
        file = super(VideoFileField, self).pre_save(model_instance, add)
        if file and not file._committed:
            # Commit the file to storage prior to saving the model
            file.save(file.name, file, save=False)
        return file

    def to_python(self, value):
        raise Exception, 'VideoFileField to_python'
        if value is None:
            return value

        tmp, path = tempfile.mkstemp()
        os.write(tmp, self._file.read(512))
        os.close(tmp)
        specs = get_video_specs(path)
        os.unlink(path)
        if not specs:
            raise exceptions.ValidationError(
                _('Uploaded file is in an unsupported format.'))

    def formfield(self, **kwargs):
        if self.read_only:        
            defaults = { 'form_class': ReadOnlyFileField }
        else:
            defaults = {}
        defaults.update(kwargs)
        return super(VideoFileField, self).formfield(**defaults)

class ConvertibleFileField(VideoFileField):
    pass

#---------------------------------------
# Model support for storing audio files
#---------------------------------------

class AudioFieldFile(FieldFile):
    """
    A file field for storing audio files. Adds methods for accessing audio metadata and tags.
    """
    @property
    def duration(self):
        try:
            return self._get_metadata()['duration']
        except MetadataError:
            return None

    @property
    def bitrate(self):
        try:
            return self._get_metadata()['bitrate']
        except MetadataError:
            return None

    @property
    def _metadata(self):
        if not hasattr(self, '_metadata_cache'):
            if not self:
                raise MetadataError
            import mutagen
            try:
                file = mutagen.File(self.path)
            except:
                raise MetadataError
            metadata = {
                'duration': datetime.timedelta(seconds=file.info.length),
                'bitrate': file.info.bitrate,
            }
            self._metadata_cache = metadata
        return self._metadata_cache

    def _get_metadata(self):
        if not hasattr(self, '_metadata_cache'):
            if not self:
                raise MetadataError
            import mutagen
            #tmp, path = tempfile.mkstemp(suffix=self.path[self.path.rfind('.'):])
            #os.write(tmp, self._file.read(512))
            #os.close(tmp)
            #file = mutagen.File(path)
            #os.unlink(path)
            try:
                file = mutagen.File(self.path)
            except:
                raise MetadataError
            metadata = {
                'duration': datetime.timedelta(seconds=file.info.length),
                'bitrate': file.info.bitrate,
            }
            self._metadata_cache = metadata
        return self._metadata_cache

    def save(self, name, content, save=True):
        # Clear stale metadata, if it exists
        if hasattr(self, '_metadata_cache'):
            del self._metadata_cache

        # Update duration and bitrate fields, if needed
        if self.field.duration_field:
            setattr(self.instance, self.field.duration_field, self.duration)
        if self.field.bitrate_field:
            setattr(self.instance, self.field.bitrate_field, self.bitrate)

        super(AudioFieldFile, self).save(name, content, save)
    save.alters_data = True

    def delete(self, save=True):
        if hasattr(self, '_metadata_cache'):
            del self._metadata_cache
        super(AudioFieldFile, self).delete(save)
    delete.alters_data = True

class AudioFileField(models.FileField):
    """
    A custom file field which creates flv copies of uploaded videos.
    """
    attr_class = AudioFieldFile

    def __init__(self, verbose_name=None, name=None, duration_field=None, bitrate_field=None, **kwargs):
        self.duration_field, self.bitrate_field = duration_field, bitrate_field
        FileField.__init__(self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.FileField}
        defaults.update(kwargs)
        return super(AudioFileField, self).formfield(**defaults)

    def to_python(self, value):
        raise Exception, 'AudioFileField to_python'
        if value is None:
            raise Exception
            return value

        import mutagen
        if not mutagen.File(StringIO(value)):
            raise exceptions.ValidationError(
                _('Uploaded file is not a valid audio file, or is in an unsupported format.'))
