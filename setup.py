#!/usr/bin/env python

import setuptools
import novaagent
import sys
import os
import stat
from shutil import copyfile

requirements = ['netifaces', 'pyxs', 'pycrypto', 'PyYaml', 'distro']
if sys.version_info[:2] < (2, 7):
    requirements.append('argparse')


test_requirements = ['mock', 'nose']
if sys.version_info[:2] < (2, 7):
    test_requirements.extend(['flake8 < 3', 'unittest2'])
else:

    test_requirements.append('flake8')

# https://stackoverflow.com/a/30463972
def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)

# https://stackoverflow.com/a/36902139
class PostInstallCommand(install):
    def run(self):
        install.run(self)
        file_from = None
        file_to = None
        is_executable = True

        dirname = os.path.dirname(__file__)

        if os.path.exists('/etc/alpine-release'):
            file_from = os.path.join(dirname, 'etc/nova-agent.alpine')
            file_to = '/etc/init.d/nova-agent'

        if file_from != None and file_to != None:
            copyfile(file_from, file_to)
            if is_executable:
                make_executable(file_to)

setuptools.setup(
    name='novaagent',
    version=novaagent.__version__,
    description=(
        'Rackspace utility for reading xenstore and configuring'
        ' guest instance on Xen server'
    ),
    author='Brian Metzler',
    author_email='brian.metzler@rackspace.com',
    install_requires=requirements,
    extras_require={
        'tests': test_requirements
    },
    cmdclass={
        'install': PostInstallCommand
    },
    entry_points={
        'console_scripts': [
            'nova-agent=novaagent.novaagent:main'
        ]
    },
    packages=[
        'novaagent',
        'novaagent.libs',
        'novaagent.common',
        'novaagent.xenstore'
    ],
    zip_safe=False
)
