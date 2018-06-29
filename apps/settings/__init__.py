import logging

logs = logging.getLogger(__name__)

try:
    from .local import *
except ImportError as e:
    logs.exception('Settings Import Error', e)
