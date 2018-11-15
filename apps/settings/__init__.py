import logging

logger = logging.getLogger(__name__)

try:
    from .local import *
except ImportError as e:
    logger.exception('Settings Import Error', e)
