import settings
import os
import re
import subprocess
import shutil
import datetime
import time
import random
import tempfile
from django.conf import settings
from django.core.mail import send_mail

    

def mail_video_errors(procout, procerr):
    message = '\nError:\n' +  procerr
    message += '\nOutput:\n' + procout
    has_format_error = procerr.find('Unknown format') != -1
    has_one_file_error =\
        procerr.find('At least one output file must be specified') != -1
    has_file_empty_error =\
        procerr.find('Invalid data found when processing input') != -1
    empty_stream_error =\
        procerr.find('Broken FLV file, which says no streams present') != -1
    if (not has_format_error) and (not has_one_file_error) and \
            (not has_file_empty_error) and (not empty_stream_error):
        send_mail('Video processing error', message, settings.SERVER_EMAIL, 
                  [a[1] for a in settings.ADMINS], fail_silently=False)

class WrongFfmpegFormat(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def make_flv_for(instance):
    """Create a Flash movie file for given Video model instance.
    """
    src_name = instance.upload_file.name
    path, ext = os.path.splitext(src_name)
    src_path = os.path.join(settings.VIDEOS_TEMP_DIR, src_name)
    upload_to = time.strftime(instance.flv_file.field.upload_to)
    dest_name = os.path.join(upload_to, os.path.basename(path) + '.flv')
    dest_path = os.path.join(settings.VIDEOS_TEMP_DIR, dest_name)
    try:
        os.makedirs(os.path.dirname(dest_path))
    except:
        pass
    if ext == '.flv':
        # File is already in FLV format, just copy it
        shutil.copy2(src_path, dest_path)        
    else:
        tmpout = tempfile.NamedTemporaryFile(mode='rw+');
        tmperr = tempfile.NamedTemporaryFile(mode='rw+');
        process = subprocess.Popen(['ffmpeg',
            '-i', src_path,
            '-acodec', 'libmp3lame',
            '-ar', '22050',
            '-ab', '32768',
            '-f', 'flv',
            '-b', '200',
            '-r', '22',
            '-s', instance.size.as_pair,
            '-y',
            dest_path
        ], stdout=tmpout, stderr=tmperr)
        stdoutdata, stderrdata = process.communicate()
        if process.returncode == 1:
            tmpout.seek(0)
            tmperr.seek(0)
            mail_video_errors(tmpout.read(), tmperr.read())
            raise WrongFfmpegFormat('invalid video format')
    subprocess.call(['flvtool2', '-U', dest_path])
    return dest_name

def take_snapshot_for(instance):
    """Grab a splash image from video at specified time position.
    """
    flv = instance.flv_file
    path, ext = os.path.splitext(flv.name)
    upload_to = time.strftime(instance.splash_image.field.upload_to)
    image_name = os.path.join(upload_to, os.path.basename(path) + '.jpg')
    
    inp = os.path.join(settings.VIDEOS_TEMP_DIR, flv.name)
    outp = os.path.join(settings.VIDEOS_TEMP_DIR, image_name)
    try:
        os.makedirs(os.path.dirname(outp))
    except:
        pass

    try:
        position = random.randint(1, instance.duration.seconds)
    except:
        position = 0
    instance.auto_position = '%s' % position

    tmpout = tempfile.NamedTemporaryFile(mode='rw+');
    tmperr = tempfile.NamedTemporaryFile(mode='rw+');
    process = subprocess.Popen(['ffmpeg',
        '-i', inp,
        '-an',
        '-ss', instance.auto_position,
        '-r', '1',
        '-vframes', '1',
        '-f', 'image2',
        '-y', outp,
        ], stdout=tmpout, stderr=tmperr)
    stdoutdata, stderrdata = process.communicate()
    # there was a problem with the video, (not supported format)
    if process.returncode == 1:
        wimage_name = None
        tmpout.seek(0)
        tmperr.seek(0)
        mail_video_errors(tmpout.read(), tmperr.read())
        raise WrongFfmpegFormat('invalid video format')
    return image_name

SPECS_RE = re.compile(r'Duration: (?P<duration>\d\d:\d\d:\d\d\.\d\d).+? bitrate: (?P<bitrate>\d+) kb/s.+? (?P<width>\d+)x(?P<height>\d+)', re.DOTALL)
VIDEO_RE = re.compile(r'Stream.+?Video: (.+)', re.DOTALL)
AUDIO_RE = re.compile(r'Stream.+?Audio: (.+)', re.DOTALL)

class MetadataError(Exception):
    pass

def get_video_specs(name=None, file=None):
    if file:
        tmp, path = tempfile.mkstemp()
        os.write(tmp, file.read(1024*1024))
        os.close(tmp)
        #os.unlink(path)
        fpath = path
    else:
        fpath = os.path.join(settings.VIDEOS_TEMP_DIR, name)


    tmpout = tempfile.NamedTemporaryFile(mode='rw+');
    tmperr = tempfile.NamedTemporaryFile(mode='rw+');
    
    process = subprocess.Popen(['ffmpeg',
        '-i', fpath,
    ], stdout=tmpout, stderr=tmperr)
    stdoutdata, stderrdata = process.communicate()
    tmpout.seek(0)
    tmperr.seek(0)
    stdoutdata = tmpout.read()
    stderrdata = tmperr.read()
    specs = { 'duration': None, 
              'width': None, 
              'height': None, 
              'bitrate': None, 
              'video': None, 
              'audio': None }
    m = SPECS_RE.search(stderrdata.replace('\n', '\r'))
    if not m:
        tmpout.seek(0)
        tmperr.seek(0)
        mail_video_errors(tmpout.read(), tmperr.read())
        raise MetadataError, stderrdata
        return None
    specs.update(m.groupdict())
    m = VIDEO_RE.search(stderrdata)
    if m:
        specs.update(m.groupdict())
    m = AUDIO_RE.search(stderrdata)
    if m:
        specs.update(m.groupdict())
    return specs
