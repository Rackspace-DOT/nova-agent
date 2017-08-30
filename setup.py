#!/usr/bin/env python

import setuptools
import novaagent
import sys


requirements = ['netifaces', 'pyxs', 'pycrypto']
if sys.version_info[:2] < (2, 7):
    requirements.append('argparse')


test_requirements = ['mock', 'nose']
if sys.version_info[:2] < (2, 7):
    test_requirements.extend(['flake8 < 3', 'unittest2'])
else:
    test_requirements.append('flake8')


setuptools.setup(
    name='novaagent',
    version=novaagent.__version__,
    description=(
        'Rackspace utility for reading xenstore and configuring'
        ' guest instance on Xen server'
    ),
    author='David Kludt',
    author_email='david.kludt@rackspace.com',
    install_requires=requirements,
    extras_require={
        'tests': test_requirements
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
