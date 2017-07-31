#!/usr/bin/env python

import setuptools
import novaagent


setuptools.setup(
    name='novaagent',
    version=novaagent.__version__,
    description=(
        'Rackspace utility for reading xenstore and configuring'
        ' guest instance on Xen server'
    ),
    author='David Kludt',
    author_email='david.kludt@rackspace.com',
    install_requires=['pyxs', 'pycrypto'],
    extra_require={
        'dev': ['netifaces'],
        'test': ['mock', 'coverage', 'flake8', 'nose']
    },
    entry_points={
        'console_scripts': [
            'nova-agent=novaagent.novaagent:main'
        ]
    },
    packages=['novaagent', 'novaagent.libs', 'novaagent.common'],
    zip_safe=False
)
