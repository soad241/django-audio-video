# Run with
# python manage.py test --settings=audio_video.tests.settings

import sys
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'audio_video.tests.settings'

from django.conf import settings
from django.test.simple import run_tests
from django.db.models.loading import load_app

test_models = [ load_app(app) for app in settings.INSTALLED_APPS ]
failures = run_tests(['audio_video'], verbosity=1)
if failures:
    sys.exit(failures)
