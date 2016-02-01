#!/usr/bin/env python

import setuptools

import novaagent

setuptools.setup(
    name='novaagent',
    version=novaagent.__version__,
    description=('Rackspace utility for reading xenstore and writing'
                 'out information on bootup'),
    author='Daniel Wallace',
    author_email='daniel.wallace@rackspace.com',
    entry_points={
        'console_scripts': [
            'nova-agent=novaagent.novaagent:main'
        ]
    },
    packages=['novaagent', 'novaagent.libs', 'novaagent.common'],
    zip_safe=False
)
