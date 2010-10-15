import settings
import os
import re
import subprocess
import shutil
import datetime
import time
import random

def make_flv_for(instance):
    """Create a Flash movie file for given Video model instance.
    """
    src_name = instance.upload_file.name
    path, ext = os.path.splitext(src_name)
    src_path = os.path.join(settings.MEDIA_ROOT, src_name)
    upload_to = time.strftime(instance.flv_file.field.upload_to)
    dest_name = os.path.join(upload_to, os.path.basename(path) + '.flv')
    dest_path = os.path.join(settings.MEDIA_ROOT, dest_name)
    try:
        os.makedirs(os.path.dirname(dest_path))
    except:
        pass
    if ext == '.flv':
        # File is already in FLV format, just copy it
        shutil.copy2(src_path, dest_path)        
    else:
        # Call ffmpeg to convert video to FLV format
        process = subprocess.Popen(['ffmpeg',
            '-i', src_path,
            '-acodec', 'libmp3lame',
            '-ar', '22050',
            '-ab', '32768',
            '-f', 'flv',
            '-s', instance.size.as_pair,
            '-y',
            dest_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdoutdata, stderrdata = process.communicate()

    # Add FLV metadata to video file
    subprocess.call(['flvtool2', '-U', dest_path])
    return dest_name

def take_snapshot_for(instance):
    """Grab a splash image from video at specified time position.
    """
    flv = instance.flv_file
    path, ext = os.path.splitext(flv.name)
    upload_to = time.strftime(instance.splash_image.field.upload_to)
    image_name = os.path.join(upload_to, os.path.basename(path) + '.jpg')
    
    inp = os.path.join(settings.MEDIA_ROOT, flv.name)
    outp = os.path.join(settings.MEDIA_ROOT, image_name)
    try:
        os.makedirs(os.path.dirname(outp))
    except:
        pass

    try:
        position = random.randint(1, instance.duration.seconds)
    except:
        position = 0
    instance.auto_position = '%s' % position

    process = subprocess.call(['ffmpeg',
        '-i', inp,
        '-an',
        '-ss', instance.auto_position,
        '-r', '1',
        '-vframes', '1',
        '-f', 'image2',
        '-y', outp,
    ])
    return image_name

SPECS_RE = re.compile(r'Duration: (?P<duration>\d\d:\d\d:\d\d\.\d\d).+? bitrate: (?P<bitrate>\d+) kb/s.+? (?P<width>\d+)x(?P<height>\d+)', re.DOTALL)
VIDEO_RE = re.compile(r'Stream.+?Video: (.+)', re.DOTALL)
AUDIO_RE = re.compile(r'Stream.+?Audio: (.+)', re.DOTALL)

class MetadataError(Exception):
    pass

def get_video_specs(name=None, file=None):
    if file:
        import tempfile
        tmp, path = tempfile.mkstemp()
        os.write(tmp, file.read(1024*1024))
        os.close(tmp)
        #os.unlink(path)
        fpath = path
    else:
        fpath = os.path.join(settings.MEDIA_ROOT, name)

    process = subprocess.Popen(['ffmpeg',
        '-i', fpath,
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = process.communicate()

    specs = { 'duration': None, 'width': None, 'height': None, 'bitrate': None, 'video': None, 'audio': None }
    m = SPECS_RE.search(stderrdata.replace('\n', '\r'))
    if not m:
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
