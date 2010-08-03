from distutils.core import setup
import os

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('audio_video'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[9:] # Strip "audio_video/" or "audio_video\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))

setup(name='django-audio-video',
      version='0.1',
      description='Storage and serving of audio and video files in Django websites',
      author='Itai Tavor',
      author_email='itai@tavor.net',
      url='http://github.com/itavor/django-audio-video/',
      package_dir={'audio_video': 'audio_video'},
      packages=packages,
      package_data={'audio_video': data_files},
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
      )
