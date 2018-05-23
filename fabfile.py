# coding=utf-8

"""
The env varibles in fabfile

"""

import re
import time
from contextlib import contextmanager as _contextmanager
from fabric.api import hosts, cd, run, with_settings, prefix, settings
from fabric.contrib.files import exists, sudo
from fabric.context_managers import hide

