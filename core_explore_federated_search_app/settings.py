""" Settings
"""
from django.conf import settings

if not settings.configured:
    settings.configure()

INSTALLED_APPS = getattr(settings, "INSTALLED_APPS", ["oauth2_provider"])

# Ensure oauth2_provider package is installed
if "oauth2_provider" not in INSTALLED_APPS:
    raise Exception("Missing 'oauth2_provider' in INSTALLED_APPS")

DATA_SORTING_FIELDS = getattr(settings, "DATA_SORTING_FIELDS", [])
