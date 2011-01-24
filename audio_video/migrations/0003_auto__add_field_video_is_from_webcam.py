# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Video.is_from_webcam'
        #db.add_column('audio_video_video', 'is_from_webcam', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)
        pass

    def backwards(self, orm):
        
        # Deleting field 'Video.is_from_webcam'
        #db.delete_column('audio_video_video', 'is_from_webcam')
        pass

    models = {
        'audio_video.audio': {
            'Meta': {'object_name': 'Audio'},
            'bitrate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'duration': ('audio_video.fields.DurationField', [], {'null': 'True', 'blank': 'True'}),
            'file': ('audio_video.fields.AudioFileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tags': ('audio_video.models.TagField', [], {'max_length': '255', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'audio_video.video': {
            'Meta': {'object_name': 'Video'},
            'auto_position': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'duration': ('audio_video.fields.DurationField', [], {'null': 'True', 'blank': 'True'}),
            'flv_file': ('audio_video.fields.VideoFileField', [], {'max_length': '100', 'blank': 'True'}),
            'height': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_from_webcam': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'size': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['audio_video.VideoSize']"}),
            'splash_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'tags': ('audio_video.models.TagField', [], {'max_length': '255', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'upload_file': ('audio_video.fields.VideoFileField', [], {'max_length': '100'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'audio_video.videosize': {
            'Meta': {'ordering': "('-width', '-height')", 'object_name': 'VideoSize'},
            'height': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['audio_video']
