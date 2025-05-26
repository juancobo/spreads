#!/usr/bin/env python3
import os
import re
import shutil
from contextlib import contextmanager
from datetime import datetime
from subprocess import check_call, check_output
from setuptools import setup
from setuptools.command.sdist import sdist as SdistCommand  # flake8: noqa
from setuptools.command.bdist_wininst import (
    bdist_wininst as WininstCommand)  # flake8: noqa

import spreads

if os.path.exists('README.rst'):
    description_long = open('README.rst').read()
else:
    description_long = """
spreads is a tool that aims to streamline your book scanning workflow.  It
takes care of every step=Setting up your capturing devices, handling the
capturing process, downloading the images to your machine, post-processing them
and finally assembling a variety of output formats.

Along the way you can always fine-tune the auto-generated results either by
supplying arguments or changing the configuration beforehand, or by inspecting
the output and applying your modifications.

It is meant to be fully customizable. This means, adding support for new
devices is made as painless as possible. You can also hook into any of the
commands by implementing one of the available plugin hooks or even implement
your own custom sub-commands.
"""

VERSION = '1.0.0dev{0}.{1}'.format(
    datetime.today().strftime('%Y%m%d'),
    check_output('git rev-parse HEAD'.split())[:4].decode('utf-8'))


def build_frontend_bundles():
    check_call(['make', '-C', 'spreadsplug/web/client', 'production',
                'development'])


class CustomSdistCommand(SdistCommand):
    @contextmanager
    def override_setup_version(self):
        # Hardcode version in distribution's setup.py
        with open('setup.py', 'r') as fp:
            old_setup = fp.read()
        new_setup = re.sub(r'VERSION = (.*?)\n\n',
                           "VERSION = '{0}'\n\n".format(VERSION),
                           old_setup, count=1, flags=re.DOTALL)
        with open('setup.py', 'w') as fp:
            fp.write(new_setup)
        yield
        with open('setup.py', 'w') as fp:
            fp.write(old_setup)

    def run(self):
        build_frontend_bundles()
        if 'git' not in VERSION:
            return SdistCommand.run(self)
        with self.override_setup_version():
            return SdistCommand.run(self)


class CustomWininstCommand(WininstCommand):
    def run(self):
        from buildmsi import build_msi
        build_frontend_bundles()
        build_msi(bitness=32)
        if not os.path.exists('./dist'):
            os.mkdir('./dist')
        shutil.copy(
            './build/msi32/spreads_{0}.exe'.format(spreads.__version__),
            './dist')

setup(
    name="spreads",
    version=VERSION,
    author="Johannes Baiter",
    author_email="johannes.baiter@gmail.com",
    url="http://spreads.readthedocs.org",
    description="Book digitization workflow suite",
    long_description=description_long,
    license="GNU AGPLv3",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        ("License :: OSI Approved :: GNU Affero General Public License v3 or "
         "later (AGPLv3+)"),
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics :: Capture",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
    ],
    keywords=[
        "digitization",
        "scanning",
        "chdk",
        "diybookscanner",
        "bookscanning",
    ],
    packages=[
        "spreads",
        "spreads.vendor",
        "spreads.vendor.huey",
        "spreads.vendor.huey.backends",
        "spreadsplug",
        "spreadsplug.dev",
        "spreadsplug.gui",
        "spreadsplug.web",
    ],
    package_data={
        'spreadsplug.gui': ['pixmaps/monk.png'],
        'spreadsplug.web': ['client/index.html', 'client/build/*']
    },
    entry_points={
        'console_scripts': [
            'spread = spreads.main:main',
        ],
        'spreadsplug.devices': [
            "chdkcamera=spreadsplug.dev.chdkcamera:CHDKCameraDevice",
            "gphoto2camera=spreadsplug.dev.gphoto2camera:GPhoto2CameraDevice",
            "dummy=spreadsplug.dev.dummy:DummyDevice"
        ],
        'spreadsplug.hooks': [
            "autorotate     =spreadsplug.autorotate:AutoRotatePlugin",
            "scantailor     =spreadsplug.scantailor:ScanTailorPlugin",
            "pdfbeads       =spreadsplug.pdfbeads:PDFBeadsPlugin",
            "djvubind       =spreadsplug.djvubind:DjvuBindPlugin",
            "tesseract      =spreadsplug.tesseract:TesseractPlugin",
            "gui            =spreadsplug.gui:GuiCommand",
            "web            =spreadsplug.web.app:WebCommands",
            "intervaltrigger=spreadsplug.intervaltrigger:IntervalTrigger",
            "hidtrigger     =spreadsplug.hidtrigger:HidTrigger",
        ]
    },
    install_requires=[
        "colorama >= 0.4.6",
        "PyYAML >= 6.0.2",
        "blinker >= 1.9.0", 
        "roman >= 4.2",
        "psutil >= 6.1.0",
        "isbnlib >= 3.10.14",
    ],
    extras_require={
        "chdkcamera": ["jpegtran-cffi >= 0.5.2", "chdkptp.py >= 0.1.3"],
        "gphoto2camera": ["gphoto2-cffi >= 0.4.3"],
        "autorotate": ["jpegtran-cffi >= 0.5.2"],
        "gui": ["PySide6 >= 6.8.0"],
        "hidtrigger": ["hidapi >= 0.14.0"],
        "web": [
            "Flask >= 3.0.3",
            "jpegtran-cffi >= 0.5.2",
            "requests >= 2.32.3",
            "zipstream-ng >= 1.7.1",
            "tornado >= 6.4.2",
            "Wand >= 0.6.13",
        ]
    },
    cmdclass={'sdist': CustomSdistCommand,
              'bdist_wininst': CustomWininstCommand},
    zip_safe=False
)
