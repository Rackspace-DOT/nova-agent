
from novaagent import libs


import novaagent
import logging
import sys


if sys.version_info[:2] >= (2, 7):
    from unittest import TestCase
else:
    from unittest2 import TestCase


try:
    from unittest import mock
except ImportError:
    import mock


class TestHelpers(TestCase):
    def setUp(self):
        logging.disable(logging.ERROR)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_version(self):
        self.assertEqual(
            novaagent.__version__,
            '2.1.10',
            'Version expected was not returned correctly'
        )

    def test_libs_init_version(self):
        temp = libs.DefaultOS()
        self.assertEqual(
            temp.version('Name', 'Value', 'Client'),
            ('0', '2.1.10'),
            'Did not get expected value on version'
        )

    def test_libs_init_features(self):
        temp = libs.DefaultOS()
        self.assertEqual(
            temp.features('Name', 'Value', 'Client'),
            (
                '0',
                'kmsactivate,resetnetwork,version,keyinit,'
                'features,password,agentupdate,injectfile'
            ),
            'Did not get expected value on features'
        )

    def test_libs_init_inject_file(self):
        temp = libs.DefaultOS()
        with mock.patch('novaagent.libs.FileInject.injectfile_cmd') as fin:
            fin.return_value = ('0', '')
            self.assertEqual(
                temp.injectfile('Name', 'Value', 'Client'),
                ('0', ''),
                'Did not get expected value on file inject'
            )

    def test_libs_init_password(self):
        temp = libs.DefaultOS()
        with mock.patch('novaagent.libs.PasswordCommands.password_cmd') as pas:
            pas.return_value = ('0', '')
            self.assertEqual(
                temp.password('Name', 'Value', 'Client'),
                ('0', ''),
                'Did not get expected value on password'
            )

    def test_libs_init_key_init(self):
        temp = libs.DefaultOS()
        with mock.patch('novaagent.libs.PasswordCommands.keyinit_cmd') as key:
            key.return_value = ('0', '')
            self.assertEqual(
                temp.keyinit('Name', 'Value', 'Client'),
                ('0', ''),
                'Did not get expected value on keyinit'
            )
