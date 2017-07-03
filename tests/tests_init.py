
from unittest import TestCase


import novaagent


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
