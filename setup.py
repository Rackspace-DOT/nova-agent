#!/usr/bin/env python

import setuptools
import novaagent
import sys
import os
from shutil import copytree
from shutil import rmtree

from zipapp import create_archive

from pathlib import Path
from setuptools import Command


PYZ_RUNPY = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from runpy import run_module
print("Running Python module: {0}.")
run_module("{0}")
""".format('novaagent')

requirements = ['netifaces', 'pyxs', 'cryptography', 'PyYaml', 'distro']
if sys.version_info[:2] < (2, 7):
    requirements.append('argparse')


test_requirements = ['mock', 'nose']
if sys.version_info[:2] < (2, 7):
    test_requirements.extend(['flake8 < 3', 'unittest2'])
else:
    test_requirements.append('flake8')


class BuildPyz(Command):
    """https://docs.python.org/3/library/zipapp.html#zipapp.create_archive ."""
    description, user_options = "Creates a zipapp.", []

    #
    def initialize_options(self):
        pass  # Dont needed, but required.

    #
    def finalize_options(self):
        pass  # Dont needed, but required.

    def run(self):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        dist_pyz = cur_dir + "/dist/pyz"
        src_pyz = cur_dir + "/build/pyz"
        try:
            rmtree("{}/novaagent".format(dist_pyz))
        except Exception:
            pass
        try:
            rmtree("{}/novaagent".format(src_pyz))
        except Exception:
            pass
        copytree("{}/novaagent".format(cur_dir),
                 os.path.join(src_pyz, "novaagent"))
        try:
            os.remove("{}/novaagent/nova-agent".format(dist_pyz))
        except Exception:
            pass
        fyle = Path(src_pyz).parent / '__main__.py'
        fyle.write_text(PYZ_RUNPY)

        Path("{}/novaagent".format(src_pyz)).mkdir(parents=True, exist_ok=True)
        target_dir = "usr/"
        Path(target_dir).mkdir(parents=True, exist_ok=True)
        pyz_requirements = requirements

        # We can't bundle cryptography in with pyz due to conflicts on
        #  different distros
        if 'cryptography' in pyz_requirements:
            pyz_requirements.remove('cryptography')

        cmd = "python3 -m pip install {} --target {}".format(
            " ".join(pyz_requirements), src_pyz)
        print("Running: {}".format(cmd))
        os.system(cmd)
        target_file = "{}nova-agent.pyz".format(target_dir)

        create_archive(src_pyz,
                       target=target_file,
                       interpreter="/usr/bin/env python3",
                       main="novaagent.novaagent:main")

        print("Created: {}".format(target_file))


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
    zip_safe=False,
    cmdclass={
        "pyz": BuildPyz
    }
)
