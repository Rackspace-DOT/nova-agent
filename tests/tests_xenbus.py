
from pyxs.client import Client
from pyxs.connection import XenBusConnection


from unittest import TestCase
from novaagent import xenbus


class TestXenBus(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        c = Client(router=xenbus.XenGuestRouter(XenBusConnection()))
        assert isinstance(c.router.connection, XenBusConnection)
        assert not c.router.thread.is_alive()
