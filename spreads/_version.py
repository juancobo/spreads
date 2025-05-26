# -*- coding: utf-8 -*-

"""Version information for spreads package."""

from datetime import datetime
from subprocess import check_output

try:
    __version__ = '1.0.0dev{0}.{1}'.format(
        datetime.today().strftime('%Y%m%d'),
        check_output(['git', 'rev-parse', 'HEAD'])[:4].decode('utf-8')
    )
except:
    __version__ = '1.0.0dev'
