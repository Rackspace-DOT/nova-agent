
from novaagent.libs import debian
from .fixtures import xen_data
from .fixtures import network


import logging
import glob
import sys
import os


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
        file_searches = [
            '/tmp/hostname*',
            '/tmp/interfaces*'
        ]
        for search in file_searches:
            route_files = glob.glob(search)
            for item in route_files:
                os.remove(item)

    def setup_temp_hostname(self):
        with open('/tmp/hostname', 'a+') as f:
            f.write('This is a test file')

    def setup_temp_interfaces(self):
        with open('/tmp/interfaces', 'a+') as f:
            f.write('#This is a test file\n')

    def test_setup_loopback(self):
        temp = debian.ServerOS()
        temp.netconfig_file = '/tmp/interfaces'
        temp._setup_loopback()

        with open('/tmp/interfaces') as f:
            written_data = f.readlines()

        for index, line in enumerate(written_data):
            self.assertEqual(
                line,
                network.DEBIAN_INTERFACES_LOOPBACK[index],
                'Written file did not match expected value'
            )

    def test_reset_network_hostname_failure(self):
        self.setup_temp_hostname()
        self.setup_temp_interfaces()
        temp = debian.ServerOS()
        temp.hostname_file = '/tmp/hostname'
        temp.netconfig_file = '/tmp/network'
        with mock.patch(
            'novaagent.libs.debian.ServerOS._setup_hostname'
        ) as hostname:
            hostname.return_value = 1, 'test_hostname'
            result = temp.resetnetwork('name', 'value', 'dummy_client')

        self.assertEqual(
            result,
            ('1', 'Error setting hostname'),
            'Result was not the expected value'
        )

    def test_reset_network_error_down(self):
        self.setup_temp_hostname()
        self.setup_temp_interfaces()
        temp = debian.ServerOS()
        temp.hostname_file = '/tmp/hostname'
        temp.netconfig_file = '/tmp/interfaces'
        with mock.patch(
            'novaagent.libs.debian.ServerOS._setup_hostname'
        ) as hostname:
            hostname.return_value = 0, 'test_hostname'
            with mock.patch('novaagent.utils.list_xenstore_macaddrs') as mac:
                mac.return_value = ['BC764E206C5B']
                with mock.patch('novaagent.utils.list_hw_interfaces') as hwint:
                    hwint.return_value = ['eth1']
                    mock_hw_address = mock.Mock()
                    mock_hw_address.side_effect = [
                        'BC764E206C5B'
                    ]
                    with mock.patch(
                        'novaagent.utils.get_hw_addr',
                        side_effect=mock_hw_address
                    ):
                        mock_interface = mock.Mock()
                        mock_interface.side_effect = [
                            xen_data.check_network_interface()
                        ]
                        with mock.patch(
                            'novaagent.utils.get_interface',
                            side_effect=mock_interface
                        ):
                            with mock.patch(
                                'novaagent.libs.debian.Popen'
                            ) as p:
                                p.return_value.communicate.return_value = (
                                    'out', 'error'
                                )
                                p.return_value.returncode = 1
                                result = temp.resetnetwork(
                                    'name',
                                    'value',
                                    'dummy_client'
                                )

        self.assertEqual(
            result,
            ('1', 'Error stopping network: eth1'),
            'Result was not the expected value'
        )
        interface_files = glob.glob('/tmp/interfaces*')
        self.assertEqual(
            len(interface_files),
            2,
            'Incorrect number of interface files'
        )

    def test_reset_network_error_up(self):
        self.setup_temp_hostname()
        self.setup_temp_interfaces()
        temp = debian.ServerOS()
        temp.hostname_file = '/tmp/hostname'
        temp.netconfig_file = '/tmp/interfaces'
        with mock.patch(
            'novaagent.libs.debian.ServerOS._setup_hostname'
        ) as hostname:
            hostname.return_value = 0, 'test_hostname'
            with mock.patch('novaagent.utils.list_xenstore_macaddrs') as mac:
                mac.return_value = ['BC764E206C5B']
                with mock.patch('novaagent.utils.list_hw_interfaces') as hwint:
                    hwint.return_value = ['eth1']
                    mock_hw_address = mock.Mock()
                    mock_hw_address.side_effect = [
                        'BC764E206C5B'
                    ]
                    with mock.patch(
                        'novaagent.utils.get_hw_addr',
                        side_effect=mock_hw_address
                    ):
                        mock_interface = mock.Mock()
                        mock_interface.side_effect = [
                            xen_data.check_network_interface()
                        ]
                        with mock.patch(
                            'novaagent.utils.get_interface',
                            side_effect=mock_interface
                        ):
                            mock_popen = mock.Mock()
                            mock_comm = mock.Mock()
                            mock_comm.return_value = ('out', 'error')
                            mock_popen.side_effect = [
                                mock.Mock(returncode=0, communicate=mock_comm),
                                mock.Mock(returncode=1, communicate=mock_comm)
                            ]
                            with mock.patch(
                                'novaagent.libs.debian.Popen',
                                side_effect=mock_popen
                            ):
                                result = temp.resetnetwork(
                                    'name',
                                    'value',
                                    'dummy_client'
                                )

        self.assertEqual(
            result,
            ('1', 'Error starting network: eth1'),
            'Result was not the expected value'
        )
        interface_files = glob.glob('/tmp/interfaces*')
        self.assertEqual(
            len(interface_files),
            2,
            'Incorrect number of interface files'
        )

    def test_reset_network_success(self):
        self.setup_temp_hostname()
        self.setup_temp_interfaces()
        temp = debian.ServerOS()
        temp.hostname_file = '/tmp/hostname'
        temp.netconfig_file = '/tmp/interfaces'
        with mock.patch(
            'novaagent.libs.debian.ServerOS._setup_hostname'
        ) as hostname:
            hostname.return_value = 0, 'test_hostname'
            with mock.patch('novaagent.utils.list_xenstore_macaddrs') as mac:
                mac.return_value = ['BC764E207572', 'BC764E206C5B']
                with mock.patch('novaagent.utils.list_hw_interfaces') as hwint:
                    hwint.return_value = ['eth0', 'eth1']
                    mock_hw_address = mock.Mock()
                    mock_hw_address.side_effect = [
                        'BC764E207572',
                        'BC764E206C5B'
                    ]
                    with mock.patch(
                        'novaagent.utils.get_hw_addr',
                        side_effect=mock_hw_address
                    ):
                        mock_interface = mock.Mock()
                        mock_interface.side_effect = [
                            network.ETH0_INTERFACE,
                            xen_data.check_network_interface()
                        ]
                        with mock.patch(
                            'novaagent.utils.get_interface',
                            side_effect=mock_interface
                        ):
                            mock_popen = mock.Mock()
                            mock_comm = mock.Mock()
                            mock_comm.return_value = ('out', 'error')
                            mock_popen.side_effect = [
                                mock.Mock(returncode=0, communicate=mock_comm),
                                mock.Mock(returncode=0, communicate=mock_comm),
                                mock.Mock(returncode=0, communicate=mock_comm),
                                mock.Mock(returncode=0, communicate=mock_comm)
                            ]
                            with mock.patch(
                                'novaagent.libs.debian.Popen',
                                side_effect=mock_popen
                            ):
                                result = temp.resetnetwork(
                                    'name',
                                    'value',
                                    'dummy_client'
                                )

        self.assertEqual(
            result,
            ('0', ''),
            'Result was not the expected value'
        )
        interface_files = glob.glob('/tmp/interfaces*')
        self.assertEqual(
            len(interface_files),
            2,
            'Incorrect number of interface files'
        )
        with open('/tmp/interfaces') as f:
            written_data = f.readlines()

        update_config = network.DEBIAN_INTERFACES_CONFIG
        del update_config[0]
        loopback = [
            '# The loopback network interface\n',
            'auto lo\n',
            'iface lo inet loopback\n',
            '\n'
        ]
        check_success = loopback + update_config
        for index, line in enumerate(written_data):
            self.assertIn(
                line,
                check_success,
                'Written file did not match expected value'
            )

    def test_interface_setup(self):
        self.setup_temp_interfaces()
        temp = debian.ServerOS()
        temp.netconfig_file = '/tmp/interfaces'
        temp_iface = network.ETH0_INTERFACE
        temp._setup_interface('eth0', temp_iface)
        temp_iface = xen_data.check_network_interface()
        temp._setup_interface('eth1', temp_iface)
        files = glob.glob('/tmp/interfaces*')
        self.assertEqual(
            len(files),
            1,
            'Did not find correct number of files'
        )
        with open('/tmp/interfaces') as f:
            written_data = f.readlines()

        for index, line in enumerate(written_data):
            self.assertEqual(
                line,
                network.DEBIAN_INTERFACES_CONFIG[index],
                'Written file did not match expected value'
            )

    def test_setup_hostname_hostname_success(self):
        self.setup_temp_hostname()
        temp = debian.ServerOS()
        temp.hostname_file = '/tmp/hostname'
        test_hostname = 'test.hostname'
        with mock.patch('novaagent.utils.get_hostname') as hostname:
            hostname.return_value = test_hostname
            with mock.patch('novaagent.libs.debian.os.path.exists') as exists:
                exists.return_value = False
                with mock.patch('novaagent.libs.debian.Popen') as popen:
                    popen.return_value.communicate.return_value = (
                        ('out', 'err')
                    )
                    popen.return_value.returncode = 0
                    return_code, hostname = temp._setup_hostname(
                        'dummy_client'
                    )

        self.assertEqual(
            hostname,
            test_hostname,
            'Did not receive expected host from function'
        )
        self.assertEqual(
            return_code,
            0,
            'Return code received was not expected value'
        )

    def test_setup_hostname_hostname_failure(self):
        self.setup_temp_hostname()
        temp = debian.ServerOS()
        temp.hostname_file = '/tmp/hostname'
        test_hostname = 'test.hostname'
        with mock.patch('novaagent.utils.get_hostname') as hostname:
            hostname.return_value = test_hostname
            with mock.patch('novaagent.libs.debian.os.path.exists') as exists:
                exists.return_value = False
                with mock.patch('novaagent.libs.debian.Popen') as popen:
                    popen.return_value.communicate.return_value = (
                        ('out', 'err')
                    )
                    popen.return_value.returncode = 1
                    return_code, hostname = temp._setup_hostname(
                        'dummy_client'
                    )

        self.assertEqual(
            hostname,
            test_hostname,
            'Did not receive expected host from function'
        )
        self.assertEqual(
            return_code,
            1,
            'Return code received was not expected value'
        )

    def test_setup_hostname_hostnamectl_success(self):
        self.setup_temp_hostname()
        temp = debian.ServerOS()
        temp.hostname_file = '/tmp/hostname'
        test_hostname = 'test.hostname'
        with mock.patch('novaagent.utils.get_hostname') as hostname:
            hostname.return_value = test_hostname
            with mock.patch('novaagent.libs.debian.os.path.exists') as exists:
                exists.return_value = True
                with mock.patch('novaagent.libs.debian.Popen') as popen:
                    popen.return_value.communicate.return_value = (
                        ('out', 'err')
                    )
                    popen.return_value.returncode = 0
                    return_code, hostname = temp._setup_hostname(
                        'dummy_client'
                    )

        self.assertEqual(
            hostname,
            test_hostname,
            'Did not receive expected host from function'
        )
        self.assertEqual(
            return_code,
            0,
            'Return code received was not expected value'
        )

    def test_setup_hostname_hostnamectl_failure(self):
        self.setup_temp_hostname()
        temp = debian.ServerOS()
        temp.hostname_file = '/tmp/hostname'
        test_hostname = 'test.hostname'
        with mock.patch('novaagent.utils.get_hostname') as hostname:
            hostname.return_value = test_hostname
            with mock.patch('novaagent.libs.debian.os.path.exists') as exists:
                exists.return_value = True
                with mock.patch('novaagent.libs.debian.Popen') as popen:
                    popen.return_value.communicate.return_value = (
                        ('out', 'err')
                    )
                    popen.return_value.returncode = 1
                    return_code, hostname = temp._setup_hostname(
                        'dummy_client'
                    )

        self.assertEqual(
            hostname,
            test_hostname,
            'Did not receive expected host from function'
        )
        self.assertEqual(
            return_code,
            1,
            'Return code received was not expected value'
        )
