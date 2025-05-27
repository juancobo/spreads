import os
import subprocess
import platform
from pathlib import Path

from setuptools.command.install import install as InstallCommand
from setuptools import setup, find_packages

CHDKPTP_PATH = Path(__file__).parent / 'chdkptp' / 'vendor' / 'chdkptp'
CHDKPTP_PATCH = Path(__file__).parent / 'chdkptp_module.diff'


class CustomInstall(InstallCommand):
    def run(self):
        # Apply patch to chdkptp
        subprocess.check_call(['patch', '-d', str(CHDKPTP_PATH), '-i',
                              str(CHDKPTP_PATCH), '-p', '1'])
        
        # Create a symbolic link to the appropriate config file based on platform
        config_file = 'config-sample-linux.mk'
        if platform.system() == 'Windows':
            config_file = 'config-sample-win32.mk'
            
        config_src = CHDKPTP_PATH / config_file
        config_dst = CHDKPTP_PATH / 'config.mk'
        
        # Handle both symlink-capable and non-symlink platforms
        try:
            os.symlink(str(config_src), str(config_dst))
        except (OSError, AttributeError):
            # On Windows or if symlinks are not supported, copy the file instead
            import shutil
            shutil.copyfile(str(config_src), str(config_dst))
            
        # Build chdkptp
        subprocess.check_call(['make', '-C', str(CHDKPTP_PATH)])
        
        # Complete the installation
        InstallCommand.run(self)


with open('README.rst', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='chdkptp.py',
    version="0.2.0",
    description="Python bindings for chdkptp (Canon CHDK PTP)",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author="Johannes Baiter",
    url="https://github.com/jbaiter/chdkptp.py",
    author_email="johannes.baiter@gmail.com",
    license='GPL',
    packages=find_packages(),
    package_data={
        "chdkptp": [
            "vendor/chdkptp/chdkptp.so",
            "vendor/chdkptp/lua/*.lua"
        ]
    },
    python_requires='>=3.6',
    install_requires=[
        "lupa >= 1.10",
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Multimedia :: Graphics :: Capture',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    cmdclass={'install': CustomInstall}
)
