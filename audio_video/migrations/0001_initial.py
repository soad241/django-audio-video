
from south.db import db
from django.db import models
from audio_video.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Audio'
        db.create_table('audio_video_audio', (
            ('description', orm['audio_video.Audio:description']),
            ('tags', orm['audio_video.Audio:tags']),
            ('title', orm['audio_video.Audio:title']),
            ('duration', orm['audio_video.Audio:duration']),
            ('file', orm['audio_video.Audio:file']),
            ('date', orm['audio_video.Audio:date']),
            ('bitrate', orm['audio_video.Audio:bitrate']),
            ('id', orm['audio_video.Audio:id']),
        ))
        db.send_create_signal('audio_video', ['Audio'])
        
        # Adding model 'Video'
        db.create_table('audio_video_video', (
            ('splash_image', orm['audio_video.Video:splash_image']),
            ('description', orm['audio_video.Video:description']),
            ('title', orm['audio_video.Video:title']),
            ('tags', orm['audio_video.Video:tags']),
            ('height', orm['audio_video.Video:height']),
            ('duration', orm['audio_video.Video:duration']),
            ('width', orm['audio_video.Video:width']),
            ('auto_position', orm['audio_video.Video:auto_position']),
            ('flv_file', orm['audio_video.Video:flv_file']),
            ('date', orm['audio_video.Video:date']),
            ('upload_file', orm['audio_video.Video:upload_file']),
            ('id', orm['audio_video.Video:id']),
            ('size', orm['audio_video.Video:size']),
        ))
        db.send_create_signal('audio_video', ['Video'])
        
        # Adding model 'VideoSize'
        db.create_table('audio_video_videosize', (
            ('width', orm['audio_video.VideoSize:width']),
            ('height', orm['audio_video.VideoSize:height']),
            ('id', orm['audio_video.VideoSize:id']),
            ('title', orm['audio_video.VideoSize:title']),
        ))
        db.send_create_signal('audio_video', ['VideoSize'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Audio'
        db.delete_table('audio_video_audio')
        
        # Deleting model 'Video'
        db.delete_table('audio_video_video')
        
        # Deleting model 'VideoSize'
        db.delete_table('audio_video_videosize')
        
    
    
    models = {
        'audio_video.audio': {
            'bitrate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'duration': ('DurationField', ["_('duration')"], {'null': 'True', 'blank': 'True'}),
            'file': ('AudioFileField', ["_('audio file')"], {'duration_field': "'duration'", 'bitrate_field': "'bitrate'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tags': ('TagField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'audio_video.video': {
            'auto_position': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'duration': ('DurationField', ["_('duration')"], {'null': 'True', 'blank': 'True'}),
            'flv_file': ('VideoFileField', ["_('final video file')"], {'read_only': 'True', 'width_field': "'width'", 'height_field': "'height'", 'blank': 'True', 'duration_field': "'duration'"}),
            'height': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'size': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['audio_video.VideoSize']"}),
            'splash_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'tags': ('TagField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'upload_file': ('VideoFileField', ["_('upload video file')"], {}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'audio_video.videosize': {
            'height': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }
    
    complete_apps = ['audio_video']
