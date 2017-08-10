
from pyxs.client import Client
from pyxs.connection import XenBusConnection


from novaagent import xenbus


import logging
import sys


if sys.version_info[:2] >= (2, 7):
    from unittest import TestCase
else:
    from unittest2 import TestCase


class TestXenBus(TestCase):
    def setUp(self):
        logging.disable(logging.ERROR)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_init(self):
        c = Client(router=xenbus.XenGuestRouter(XenBusConnection()))
        assert isinstance(c.router.connection, XenBusConnection)
        assert not c.router.thread.is_alive()
