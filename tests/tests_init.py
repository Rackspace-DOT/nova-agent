
from unittest import TestCase
from novaagent import libs

import novaagent
import mock


class TestHelpers(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_version(self):
        self.assertEqual(
            novaagent.__version__,
            '2.0.0',
            'Version expected was not returned correctly'
        )

    def test_libs_init_version(self):
        temp = libs.DefaultOS()
        self.assertEqual(
            temp.version('Name', 'Value'),
            ('0', '2.0.0'),
            'Did not get expected value on version'
        )

    def test_libs_init_features(self):
        temp = libs.DefaultOS()
        self.assertEqual(
            temp.features('Name', 'Value'),
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
                temp.injectfile('Name', 'Value'),
                ('0', ''),
                'Did not get expected value on file inject'
            )

    def test_libs_init_password(self):
        temp = libs.DefaultOS()
        with mock.patch('novaagent.libs.PasswordCommands.password_cmd') as pas:
            pas.return_value = ('0', '')
            self.assertEqual(
                temp.password('Name', 'Value'),
                ('0', ''),
                'Did not get expected value on password'
            )

    def test_libs_init_key_init(self):
        temp = libs.DefaultOS()
        with mock.patch('novaagent.libs.PasswordCommands.keyinit_cmd') as key:
            key.return_value = ('0', '')
            self.assertEqual(
                temp.keyinit('Name', 'Value'),
                ('0', ''),
                'Did not get expected value on keyinit'
            )
