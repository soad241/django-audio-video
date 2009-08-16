from models import *
from widgets import AdminVideoWidget

from django.contrib import admin
from django.db import models

class VideoSizeAdmin(admin.ModelAdmin):
    list_display = ('title', 'width', 'height')

class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'upload_file', 'size', 'duration', 'date')
    #exclude = ('flv_file',)
    save_on_top = True
    formfield_overrides = {
        VideoFileField: { 'widget': AdminVideoWidget },
        models.ImageField: { 'widget': admin.widgets.AdminFileWidget },
    }
    fields = ('title', 'description', 'size', 'upload_file', 'flv_file',
        'splash_image', 'auto_position', 'date', 'tags')

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'flv_file':
            kwargs['widget'] = AdminVideoWidget
        return super(VideoAdmin, self).formfield_for_dbfield(db_field, **kwargs)

class AudioAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'file', 'duration', 'bitrate')
    save_on_top = True
    formfield_overrides = {
        AudioFileField: { 'widget': admin.widgets.AdminFileWidget },
    }

admin.site.register(Video, VideoAdmin)
admin.site.register(Audio, AudioAdmin)
admin.site.register(VideoSize, VideoSizeAdmin)
