import os

DIRNAME = os.path.dirname(__file__)

DEFAULT_CHARSET = 'utf-8'

DATABASE_ENGINE = 'sqlite3'

MEDIA_ROOT = os.path.join(DIRNAME, 'static/')
MEDIA_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/media/'

ROOT_URLCONF = 'audio_video.tests.urls'

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'tagging',
    'sorl.thumbnail',
    'audio_video',
    'audio_video.tests',
)

SITE_ID = 1
CACHE_TIMEOUT = 0
