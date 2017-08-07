
from novaagent.libs import redhat


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
        pass

    def tearDown(self):
        pass

    def test_redhat_kmsactivate(self):
        temp = redhat.ServerOS()
        with mock.patch('novaagent.common.kms.kms_activate') as kms:
            kms.return_value = ("0", "")
            message = temp.kmsactivate('name', 'value', 'client')

        self.assertEqual(
            ("0", ""),
            message,
            'Return value was not what was expected'
        )
