import os
import re
import subprocess

SPECS_RE = re.compile(r'Duration: (?P<duration>\d\d:\d\d:\d\d\.\d\d).+?(?P<width>\d+)x(?P<height>\d+)', re.DOTALL)

def get_video_specs(name):
    #fpath = os.path.join(settings.MEDIA_ROOT, name)
    fpath = name
    process = subprocess.Popen(['ffmpeg',
        '-i', fpath,
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = process.communicate()
    
    m = SPECS_RE.search(stderrdata)
    return {
        'duration': m.group('duration'),
        'width': m.group('width'),
        'height': m.group('height'),
    }

print get_video_specs('/opt/webapps/mmyc/static/video/upload/video.flv')
