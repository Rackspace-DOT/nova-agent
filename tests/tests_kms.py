
from novaagent.common import kms
from unittest import TestCase
from .fixtures import kms_data

import mock
import glob
import os


class TestHelpers(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        files = glob.glob('/tmp/up2date*')
        for item in files:
            os.remove(item)

    def test_register_with_rhn_success(self):
        with open('/tmp/systemid', 'a+') as f:
            f.write('This is a test file')

        kms.SYSTEMID_PATH = '/tmp/systemid'
        with mock.patch('novaagent.common.kms.subprocess.Popen') as popen:
            popen.return_value.pip = 99
            with mock.patch('novaagent.common.kms.os.waitpid') as waitpid:
                waitpid.return_value = ('', 0)
                message = kms.register_with_rhn('activation_key', 'profile')

        self.assertEqual(
            message,
            None,
            'Data was returned when should not have been'
        )

    def test_register_with_rhn_failure(self):
        with open('/tmp/systemid', 'a+') as f:
            f.write('This is a test file')

        kms.SYSTEMID_PATH = '/tmp/systemid'
        with mock.patch('novaagent.common.kms.subprocess.Popen') as popen:
            popen.return_value.pip = 99
            with mock.patch('novaagent.common.kms.os.waitpid') as waitpid:
                waitpid.return_value = ('Error registering', 1)
                message = kms.register_with_rhn('activation_key', 'profile')

        self.assertEqual(
            message,
            ("500", "Couldn't activate with RHN: 1"),
            'Data was returned when should not have been'
        )

    def test_configure_up2date(self):
        up2date = kms.configure_up2date(['iadproxy.rhn.rackspace.com'])
        kms.UP2DATE_PATH = '/etc/sysconfig/rhn/up2date'
        self.assertEqual(
            up2date.get('/etc/sysconfig/rhn/up2date'),
            kms_data.UP2DATE_RETURN,
            'Up2date data was not the expected value'
        )

    def test_kms_activate(self):
        test_data = {
            'activation_key': 'activation_key',
            'profile': 'kms_profile',
            'domains': 'iadproxy.rhn.rackspace.com'
        }
        kms.UP2DATE_PATH = '/tmp/up2date'
        with mock.patch('novaagent.common.kms.register_with_rhn') as reg:
            reg.return_value = None
            success = kms.kms_activate(test_data)

        self.assertEqual(
            success,
            ("0", ""),
            'Return value was not expected value'
        )
        files = glob.glob('/tmp/up2date*')
        self.assertEqual(
            len(files),
            1,
            'Did not find written file'
        )
        with open('/tmp/up2date') as f:
            written_data = f.readlines()

        for index, line in enumerate(written_data):
            self.assertEqual(
                line,
                kms_data.UP2DATE_READLINES[index],
                'Written file did not match expected value'
            )

    def test_kms_activate_error(self):
        test_data = {
            'activation_key': 'activation_key',
            'profile': 'kms_profile',
            'domains': 'iadproxy.rhn.rackspace.com'
        }
        kms.UP2DATE_PATH = '/tmp/up2date'
        with mock.patch('novaagent.common.kms.register_with_rhn') as reg:
            reg.return_value = ("500", "Couldn't activate with RHN")
            success = kms.kms_activate(test_data)

        self.assertEqual(
            success,
            ("500", "Couldn't activate with RHN"),
            'Return value was not expected value'
        )
        files = glob.glob('/tmp/up2date*')
        self.assertEqual(
            len(files),
            1,
            'Did not find written file'
        )
        with open('/tmp/up2date') as f:
            written_data = f.readlines()

        for index, line in enumerate(written_data):
            self.assertEqual(
                line,
                kms_data.UP2DATE_READLINES[index],
                'Written file did not match expected value'
            )
