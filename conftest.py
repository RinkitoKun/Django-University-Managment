import os
import django
import pytest

os.environ['DJANGO_SETTINGS_MODULE'] = 'your_project_name.settings'
django.setup()