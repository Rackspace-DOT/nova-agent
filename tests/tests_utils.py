
from .fixtures import utils_data
from .fixtures import xen_data
from novaagent import utils


from socket import error as socket_error


import logging
import socket
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


class ClientTest(object):
    """ Test class used for client mock """
    def __init__(self, return_value):
        self.return_data = return_value

    def list(self, path):
        return self.return_data

    def read(self, path):
        return self.return_data

    def write(self, event, data):
        return self.return_data

    def delete(self, path):
        return self.return_data


class TestHelpers(TestCase):
    def setUp(self):
        logging.disable(logging.ERROR)
        if not os.path.exists('/tmp/ifcfg-eth0'):
            with open('/tmp/ifcfg-eth0', 'a+') as f:
                f.write('This is a test file')
                os.utime('/tmp/ifcfg-eth0', None)

    def tearDown(self):
        logging.disable(logging.NOTSET)
        files = glob.glob('/tmp/ifcfg-eth0*')
        for item in files:
            os.remove(item)

    def test_get_hostname_success(self):
        client = ClientTest(xen_data.get_hostname(True))
        hostname = utils.get_hostname(client)
        self.assertEqual(
            hostname,
            'test-server',
            'Hostname does not match expected ouput'
        )

    def test_get_hostname_success_socket(self):
        with mock.patch(
            'novaagent.utils.xenstore.xenstore_read',
            side_effect=ValueError
        ):
            with mock.patch('novaagent.utils.socket') as get:
                get.gethostname.return_value = (
                    xen_data.get_hostname(False)
                )
                hostname = utils.get_hostname('dummy_client')

        self.assertEqual(
            hostname,
            'test-server',
            'Hostname does not match expected ouput'
        )

    def test_get_hostname_success_popen(self):
        with mock.patch('novaagent.xenstore.xenstore.Popen') as popen:
            popen.return_value.communicate.return_value = (
                utils_data.get_hostname(True)
            )
            popen.return_value.returncode = 0
            hostname = utils.get_hostname(None)

        self.assertEqual(
            hostname,
            'test-server',
            'Hostname does not match expected ouput'
        )

    def test_get_hostname_failure_popen(self):
        with mock.patch('novaagent.xenstore.xenstore.Popen') as popen:
            popen.return_value.communicate.return_value = (b'', '')
            popen.return_value.returncode = 1
            with mock.patch('novaagent.utils.socket') as get:
                get.gethostname.return_value = (
                    utils_data.get_hostname(False)
                )

                hostname = utils.get_hostname(None)

        self.assertEqual(
            hostname,
            'test-server',
            'Hostname does not match expected ouput'
        )

    def test_get_hostname_exception_popen(self):
        with mock.patch(
            'novaagent.xenstore.xenstore.Popen',
            side_effect=ValueError
        ):
            with mock.patch('novaagent.utils.socket') as get:
                get.gethostname.return_value = (
                    utils_data.get_hostname(False)
                )
                hostname = utils.get_hostname(None)

        self.assertEqual(
            hostname,
            'test-server',
            'Hostname does not match expected ouput'
        )

    def test_list_host_xen_events(self):
        check_events = ['748dee41-c47f-4ec7-b2cd-037e51da4031']
        client = ClientTest(xen_data.get_xen_host_events())
        event_list = utils.list_xen_events(client)
        self.assertEqual(
            event_list,
            check_events,
            'Event list does not match expected list'
        )

    def test_list_host_xen_events_exception(self):
        client = ClientTest(None)
        event_list = utils.list_xen_events(client)
        self.assertEqual(
            event_list,
            [],
            'Event list should be an empty list with exception'
        )

    def test_list_host_xen_events_popen(self):
        check_events = ['748dee41-c47f-4ec7-b2cd-037e51da4031']
        with mock.patch('novaagent.xenstore.xenstore.Popen') as popen:
            popen.return_value.communicate.return_value = (
                utils_data.get_xen_host_events()
            )
            popen.return_value.returncode = 0
            event_list = utils.list_xen_events(None)

        self.assertEqual(
            event_list,
            check_events,
            'Event list does not match expected list'
        )

    def test_list_host_xen_events_failure_popen(self):
        with mock.patch('novaagent.xenstore.xenstore.Popen') as popen:
            popen.return_value.communicate.return_value = (b'', '')
            popen.return_value.returncode = 1

            event_list = utils.list_xen_events(None)

        self.assertEqual(
            event_list,
            [],
            'Event list does not match expected list after failure'
        )

    def test_list_host_xen_events_popen_exception(self):
        with mock.patch(
            'novaagent.xenstore.xenstore.Popen',
            side_effect=ValueError
        ):
            event_list = utils.list_xen_events(None)

        self.assertEqual(
            event_list,
            [],
            'Event list should be an empty list with exception'
        )

    def test_get_host_event(self):
        host_event_id = '748dee41-c47f-4ec7-b2cd-037e51da4031'
        event_check = {
            "name": "keyinit",
            "value": "68436575764933852815830951574296"
        }
        client = ClientTest(xen_data.get_xen_host_event_details())
        event_details = utils.get_xen_event(host_event_id, client)
        self.assertEqual(
            event_check,
            event_details,
            'Event details do not match expected value'
        )

    def test_get_host_event_exception(self):
        host_event_id = '748dee41-c47f-4ec7-b2cd-037e51da4031'
        client = ClientTest(None)
        event_details = utils.get_xen_event(host_event_id, client)
        self.assertEqual(
            event_details,
            None,
            'Event details should be None on exception'
        )

    def test_get_host_event_popen(self):
        host_event_id = '748dee41-c47f-4ec7-b2cd-037e51da4031'
        event_check = {
            "name": "keyinit",
            "value": "68436575764933852815830951574296"
        }
        with mock.patch('novaagent.xenstore.xenstore.Popen') as popen:
            popen.return_value.communicate.return_value = (
                utils_data.get_xen_host_event_details()
            )
            popen.return_value.returncode = 0
            event_details = utils.get_xen_event(host_event_id, None)

        self.assertEqual(
            event_check,
            event_details,
            'Event details do not match expected value'
        )

    def test_get_host_event_failure_popen(self):
        host_event_id = '748dee41-c47f-4ec7-b2cd-037e51da4031'
        with mock.patch('novaagent.xenstore.xenstore.Popen') as popen:
            popen.return_value.communicate.return_value = (b'', '')
            popen.return_value.returncode = 1

            event_details = utils.get_xen_event(host_event_id, None)

        self.assertEqual(
            event_details,
            None,
            'Event details do not match expected value after failure'
        )

    def test_get_host_event_popen_exception(self):
        host_event_id = '748dee41-c47f-4ec7-b2cd-037e51da4031'
        with mock.patch(
            'novaagent.xenstore.xenstore.Popen',
            side_effect=ValueError
        ):
            event_details = utils.get_xen_event(host_event_id, None)

        self.assertEqual(
            event_details,
            None,
            'Event details should be None on exception'
        )

    def test_remove_xenhost_event_failure(self):
        host_event_id = '748dee41-c47f-4ec7-b2cd-037e51da4031'
        success = utils.remove_xenhost_event(host_event_id, 'dummy_client')
        self.assertEqual(
            success,
            False,
            'Return value was not False on failure'
        )

    def test_remove_xenhost_event_success(self):
        host_event_id = '748dee41-c47f-4ec7-b2cd-037e51da4031'
        client = ClientTest('')
        success = utils.remove_xenhost_event(host_event_id, client)
        self.assertEqual(
            success,
            True,
            'Return value was not True on success'
        )

    def test_remove_xenhost_event_success_popen(self):
        host_event_id = '748dee41-c47f-4ec7-b2cd-037e51da4031'
        with mock.patch('novaagent.xenstore.xenstore.Popen') as popen:
            popen.return_value.communicate.return_value = (b'', '')
            popen.return_value.returncode = 0

            success = utils.remove_xenhost_event(host_event_id, None)

        self.assertEqual(
            success,
            True,
            'Return value was not True on success'
        )

    def test_remove_xenhost_event_failure_popen(self):
        host_event_id = '748dee41-c47f-4ec7-b2cd-037e51da4031'
        with mock.patch('novaagent.xenstore.xenstore.Popen') as popen:
            popen.return_value.communicate.return_value = (b'', '')
            popen.return_value.returncode = 1

            success = utils.remove_xenhost_event(host_event_id, None)

        self.assertEqual(
            success,
            False,
            'Return value was not False on failure'
        )

    def test_remove_xenhost_event_exception_popen(self):
        host_event_id = '748dee41-c47f-4ec7-b2cd-037e51da4031'
        with mock.patch(
            'novaagent.xenstore.xenstore.Popen',
            side_effect=ValueError
        ):
            success = utils.remove_xenhost_event(host_event_id, None)

        self.assertEqual(
            success,
            False,
            'Return value was not False on exception'
        )

    def test_write_xenguest_event_success(self):
        event_uuid = '748dee41-c47f-4ec7-b2cd-037e51da4031'
        client = ClientTest('')
        write_data = {"message": "", "returncode": "0"}
        success = utils.update_xenguest_event(event_uuid, write_data, client)
        self.assertEqual(
            success,
            True,
            'Return value was not True on success'
        )

    def test_write_xenguest_event_failure(self):
        event_uuid = '748dee41-c47f-4ec7-b2cd-037e51da4031'
        write_data = {"message": "", "returncode": "0"}
        success = utils.update_xenguest_event(
            event_uuid,
            write_data,
            'dummy_client'
        )
        self.assertEqual(
            success,
            False,
            'Return value was not False on failure'
        )

    def test_write_xenguest_event_success_popen(self):
        event_uuid = '748dee41-c47f-4ec7-b2cd-037e51da4031'
        write_data = {"message": "", "returncode": "0"}
        with mock.patch('novaagent.xenstore.xenstore.Popen') as popen:
            popen.return_value.communicate.return_value = (b'', '')
            popen.return_value.returncode = 0

            success = utils.update_xenguest_event(event_uuid, write_data, None)

        self.assertEqual(
            success,
            True,
            'Return value was not True on success'
        )

    def test_write_xenguest_event_failure_popen(self):
        event_uuid = '748dee41-c47f-4ec7-b2cd-037e51da4031'
        write_data = {"message": "", "returncode": "0"}
        with mock.patch('novaagent.xenstore.xenstore.Popen') as popen:
            popen.return_value.communicate.return_value = (b'', '')
            popen.return_value.returncode = 1

            success = utils.update_xenguest_event(event_uuid, write_data, None)
        self.assertEqual(
            success,
            False,
            'Return value was not False on failure'
        )

    def test_write_xenguest_event_exception_popen(self):
        event_uuid = '748dee41-c47f-4ec7-b2cd-037e51da4031'
        write_data = {"message": "", "returncode": "0"}
        with mock.patch(
            'novaagent.xenstore.xenstore.Popen',
            side_effect=ValueError
        ):
            success = utils.update_xenguest_event(event_uuid, write_data, None)

        self.assertEqual(
            success,
            False,
            'Return value was not False on failure'
        )

    def test_network_get_interfaces_success(self):
        mac_address = 'BC764E206C5B'
        client = ClientTest(xen_data.get_network_interface())
        network_info = utils.get_interface(mac_address, client)
        self.assertEqual(
            network_info,
            xen_data.check_network_interface(),
            'Network info returned was not the expected value'
        )

    def test_network_get_interfaces_failure(self):
        mac_address = 'BC764E206C5B'
        client = ClientTest(None)
        network_info = utils.get_interface(mac_address, client)
        self.assertEqual(
            network_info,
            None,
            'Network info should be None on error'
        )

    def test_network_get_interfaces_success_popen(self):
        mac_address = 'BC764E206C5B'
        with mock.patch('novaagent.xenstore.xenstore.Popen') as popen:
            popen.return_value.communicate.return_value = (
                utils_data.get_network_interface()
            )
            popen.return_value.returncode = 0

            network_info = utils.get_interface(mac_address, None)

        self.assertEqual(
            network_info,
            xen_data.check_network_interface(),
            'Network info returned was not the expected value'
        )

    def test_network_get_interfaces_failure_popen(self):
        mac_address = 'BC764E206C5B'
        with mock.patch('novaagent.xenstore.xenstore.Popen') as popen:
            popen.return_value.communicate.return_value = (b'', '')
            popen.return_value.returncode = 1

            network_info = utils.get_interface(mac_address, None)

        self.assertEqual(
            network_info,
            None,
            'Network info returned was not the expected value'
        )

    def test_network_get_interfaces_exception_popen(self):
        mac_address = 'BC764E206C5B'
        with mock.patch(
            'novaagent.xenstore.xenstore.Popen',
            side_effect=ValueError
        ):

            network_info = utils.get_interface(mac_address, None)

        self.assertEqual(
            network_info,
            None,
            'Network info returned was not the expected value'
        )

    def test_network_get_provider_success(self):
        client = ClientTest(b'Test Provider')
        provider = utils.get_provider(client)
        self.assertEqual(
            provider,
            'Test Provider',
            'Providers do not match expected value'
        )

    def test_network_get_provider_exception(self):
        client = ClientTest(None)
        provider = utils.get_provider(client)
        self.assertEqual(
            provider,
            None,
            'Provider should have been None'
        )

    def test_network_get_provider_empty(self):
        client = ClientTest(b'')
        provider = utils.get_provider(client)
        self.assertEqual(
            provider,
            '',
            'Provider should have been an empty string'
        )

    def test_network_get_provider_success_popen(self):
        with mock.patch('novaagent.xenstore.xenstore.Popen') as popen:
            popen.return_value.communicate.return_value = (
                b'Test Provider', b''
            )
            popen.return_value.returncode = 0
            provider = utils.get_provider(None)

        self.assertEqual(
            provider,
            'Test Provider',
            'Provider does not match expected value'
        )

    def test_network_get_provider_exception_popen(self):
        with mock.patch(
            'novaagent.xenstore.xenstore.Popen',
            side_effect=ValueError
        ):
            provider = utils.get_provider(None)

        self.assertEqual(
            provider,
            None,
            'Provider returned should be None'
        )

    def test_network_get_provider_failure_popen(self):
        with mock.patch('novaagent.xenstore.xenstore.Popen') as popen:
            popen.return_value.communicate.return_value = (b'', '')
            popen.return_value.returncode = 1

            provider = utils.get_provider(None)

        self.assertEqual(
            provider,
            None,
            'Provider returned should be None'
        )

    def test_network_get_mac_addresses_success(self):
        check_mac_addrs = ['BC764E206C5B', 'BC764E206C5A']
        client = ClientTest(xen_data.get_mac_addresses())
        mac_addrs = utils.list_xenstore_macaddrs(client)
        self.assertEqual(
            mac_addrs,
            check_mac_addrs,
            'Mac addrs returned do not match expected value'
        )

    def test_network_get_mac_addresses_exception(self):
        client = ClientTest(None)
        mac_addrs = utils.list_xenstore_macaddrs(client)
        self.assertEqual(
            mac_addrs,
            [],
            'Mac addrs returned is not empty list after error'
        )

    def test_network_get_mac_addresses_failure(self):
        client = ClientTest([])
        mac_addrs = utils.list_xenstore_macaddrs(client)
        self.assertEqual(
            mac_addrs,
            [],
            'Mac addrs returned is not empty list after error'
        )

    def test_network_get_mac_addresses_success_popen(self):
        check_mac_addrs = ['BC764E206C5B', 'BC764E206C5A']
        with mock.patch('novaagent.xenstore.xenstore.Popen') as popen:
            popen.return_value.communicate.return_value = (
                utils_data.get_mac_addresses()
            )
            popen.return_value.returncode = 0

            mac_addrs = utils.list_xenstore_macaddrs(None)

        self.assertEqual(
            mac_addrs,
            check_mac_addrs,
            'Mac addrs returned do not match expected value'
        )

    def test_network_get_mac_addresses_exception_popen(self):
        with mock.patch(
            'novaagent.xenstore.xenstore.Popen',
            side_effect=ValueError
        ):
            mac_addrs = utils.list_xenstore_macaddrs(None)

        self.assertEqual(
            mac_addrs,
            [],
            'Mac addrs returned is not empty list after popen exception'
        )

    def test_network_get_mac_addresses_failure_popen(self):
        with mock.patch('novaagent.xenstore.xenstore.Popen') as popen:
            popen.return_value.communicate.return_value = (b'', '')
            popen.return_value.returncode = 1

            mac_addrs = utils.list_xenstore_macaddrs(None)

        self.assertEqual(
            mac_addrs,
            [],
            'Mac addrs returned is not empty list after popen error'
        )

    def test_get_os_interfaces(self):
        interfaces = ['lo', 'eth1', 'eth0']
        with mock.patch('novaagent.utils.os.path.exists') as os_path:
            os_path.return_value = True
            with mock.patch('novaagent.utils.os.listdir') as list_dir:
                list_dir.return_value = interfaces

                list_interfaces = utils.list_hw_interfaces()

        self.assertEqual(
            interfaces,
            list_interfaces,
            'Interfaces returned do not match expected return'
        )

    def test_get_os_interfaces_netifaces(self):
        interfaces = ['lo', 'eth1', 'eth0']
        with mock.patch('novaagent.utils.os.path.exists') as os_path:
            os_path.return_value = False
            with mock.patch('novaagent.utils.netifaces.interfaces') as netif:
                netif.return_value = interfaces

                list_interfaces = utils.list_hw_interfaces()

        self.assertEqual(
            interfaces,
            list_interfaces,
            'Interfaces returned do not match expected return'
        )

    def test_get_mac_address_from_system_string(self):
        check_mac_addr = 'BC764E2012B3'
        with mock.patch('novaagent.utils.socket.socket.fileno') as fileno:
            fileno.return_value = 3
            with mock.patch('novaagent.utils.fcntl.ioctl') as get_hex:
                get_hex.return_value = xen_data.FNCTL_INFO_STRING
                mac_address = utils.get_hw_addr('eth1')

        self.assertEqual(
            check_mac_addr,
            mac_address,
            'Mac addresses returned does not match expected value'
        )

    def test_get_mac_address_from_system_bytes(self):
        check_mac_addr = 'BC764E2012B3'
        with mock.patch('novaagent.utils.socket.socket.fileno') as fileno:
            fileno.return_value = 3
            with mock.patch('novaagent.utils.fcntl.ioctl') as get_hex:
                get_hex.return_value = xen_data.FCNTL_INFO_BYTES
                mac_address = utils.get_hw_addr('eth1')

        self.assertEqual(
            check_mac_addr,
            mac_address,
            'Mac addresses returned does not match expected value'
        )

    def test_get_mac_address_from_system_error(self):
        with mock.patch('novaagent.utils.socket.socket.fileno') as fileno:
            fileno.return_value = 3
            with mock.patch('novaagent.utils.fcntl.ioctl') as get_hex:
                get_hex.side_effect = IOError
                utils.HAS_NETIFACES = False
                mac_address = utils.get_hw_addr('eth1')

        self.assertEqual(
            False,
            mac_address,
            'Mac address returned should be false on error'
        )

    def test_get_mac_address_from_system_netifaces(self):
        check_mac_addr = 'BC764E205A79'
        with mock.patch('novaagent.utils.socket.socket.fileno') as fileno:
            fileno.return_value = 3
            with mock.patch('novaagent.utils.fcntl.ioctl') as get_hex:
                get_hex.side_effect = IOError
                with mock.patch('novaagent.utils.netifaces') as interfaces:
                    interfaces.ifaddresses.return_value = (
                        xen_data.get_iface_from_netifaces()
                    )
                    interfaces.AF_LINK = 17
                    utils.HAS_NETIFACES = True
                    mac_address = utils.get_hw_addr('eth1')

        self.assertEqual(
            check_mac_addr,
            mac_address,
            'Mac addresses returned does not match expected value'
        )

    def test_get_mac_address_from_system_netifaces_failure(self):
        with mock.patch('novaagent.utils.socket.socket.fileno') as fileno:
            fileno.return_value = 3
            with mock.patch('novaagent.utils.fcntl.ioctl') as get_hex:
                get_hex.side_effect = IOError
                with mock.patch('novaagent.utils.netifaces') as interfaces:
                    interfaces.ifaddresses.return_value = (
                        xen_data.get_iface_from_netifaces()
                    )
                    interfaces.AF_LINK = 99
                    utils.HAS_NETIFACES = True
                    mac_address = utils.get_hw_addr('eth1')

        self.assertEqual(
            False,
            mac_address,
            'Mac addresses returned should be false on error'
        )

    def test_netmask_to_prefix_24(self):
        cidr = utils.netmask_to_prefix('255.255.255.0')
        self.assertEqual(
            cidr,
            24,
            'Cidr returned does not match expected value'
        )
        cidr = utils.netmask_to_prefix('255.255.0.0')
        self.assertEqual(
            cidr,
            16,
            'Cidr returned does not match expected value'
        )

    def test_network_remove_files(self):
        net_config_dir = '/etc/sysconfig/network-scripts'
        interface_file_prefix = 'ifcfg-'

        with mock.patch('novaagent.utils.os.listdir') as listdir:
            listdir.return_value = ['lo', 'eth0']
            with mock.patch('novaagent.utils.glob.glob') as files:
                files.return_value = [
                    '/etc/sysconfig/network-scripts/ifcfg-eth1',
                    '/etc/sysconfig/network-scripts/ifcfg-lo',
                    '/etc/sysconfig/network-scripts/ifcfg-eth0'
                ]
                remove_files = utils.get_ifcfg_files_to_remove(
                    net_config_dir,
                    interface_file_prefix
                )

        self.assertEqual(
            remove_files,
            ['/etc/sysconfig/network-scripts/ifcfg-eth1'],
            'Remove files returned is not the expected value'
        )

    def test_move_interface_file_for_backup(self):
        rename_file = '/tmp/ifcfg-eth0'
        utils.backup_file(rename_file)

        files = glob.glob('/tmp/ifcfg-eth0.*.*.bak')
        self.assertEqual(
            len(files),
            1,
            'Did not find any files'
        )
        self.assertIn(
            'ifcfg-eth0',
            files[0],
            'Did not find the original filename in renamed file path'
        )

    def test_move_interface_file_for_backup_no_file(self):
        rename_file = '/tmp/ifcfg-eth0'
        os.remove(rename_file)
        utils.backup_file(rename_file)
        assert True, 'Move interface did not generate error'

    def test_rename_interface_file_success(self):
        rename_file = '/tmp/ifcfg-eth0'
        utils.backup_file(rename_file)

        files = glob.glob('/tmp/ifcfg-eth0.*.*.bak')
        self.assertEqual(
            len(files),
            1,
            'Did not find any files'
        )
        self.assertIn(
            'ifcfg-eth0',
            files[0],
            'Did not find the original filename in renamed file path'
        )

    def test_backup_file_failure(self):
        rename_file = '/tmp/ifcfg-eth0'
        os.remove(rename_file)
        utils.backup_file(rename_file)
        assert True, 'Move interface did not generate error'

    def test_encoding_to_bytes(self):
        test_string = 'this is a test'
        compare_string = b'this is a test'
        test = utils.encode_to_bytes(test_string)
        self.assertEqual(
            compare_string,
            test,
            'Byte strings do not match as expected'
        )

    def test_notification_systemd(self):
        with mock.patch('novaagent.utils.systemd_status') as mock_status:
            try:
                utils.send_notification('systemd', 'notify')
                self.assertTrue(mock_status.called)
            except Exception:
                assert False, 'systemd notification failed to complete'

    def test_notification_upstart(self):
        try:
            with mock.patch('os.kill') as mock_kill:
                utils.send_notification('upstart', None)
                self.assertTrue(mock_kill.called)
        except Exception:
            assert False, 'upstart notification failed to complete'

    def test_notify_empty_address(self):
        address = None
        socket = None
        bad_address, bad_socket = utils.notify_socket()
        self.assertEqual(
            bad_address,
            address,
            'Did not get expected value for address'
        )
        self.assertEqual(
            bad_socket,
            socket,
            'Did not get expected value for socket'
        )

    def test_notify_bad_length(self):
        address = None
        socket = None
        with mock.patch.dict(os.environ, {'NOTIFY_SOCKET': '1'}):
            bad_address, bad_socket = utils.notify_socket()

        self.assertEqual(
            bad_address,
            address,
            'Did not get expected value for address'
        )
        self.assertEqual(
            bad_socket,
            socket,
            'Did not get expected value for socket'
        )

    def test_notify_incorrect_starter(self):
        address = None
        socket = None
        with mock.patch.dict(os.environ, {'NOTIFY_SOCKET': '111'}):
            bad_address, bad_socket = utils.notify_socket()

        self.assertEqual(
            bad_address,
            address,
            'Did not get expected value for address'
        )
        self.assertEqual(
            bad_socket,
            socket,
            'Did not get expected value for socket'
        )

    def test_notify_complete(self):
        address = '\x00novaagenttest'
        socket = 'mock_socket'
        with mock.patch.dict(os.environ, {'NOTIFY_SOCKET': '@novaagenttest'}):
            with mock.patch(
                'novaagent.utils.socket'
            ) as mock_socket:
                mock_socket.socket.return_value = 'mock_socket'
                good_address, good_socket = utils.notify_socket()

        self.assertEqual(
            good_address,
            address,
            'Did not get expected value for address'
        )
        self.assertEqual(
            good_socket,
            socket,
            'Did not get expected value for socket'
        )

    def test_systemd_status_bad_address(self):
        address = None
        sock = None
        status = 'Test'
        self.assertFalse(
            utils.systemd_status(address, sock, status),
            'Error on empty values'
        )

    def test_systemd_status_completed(self):
        address = 'address'
        status = 'Test'
        mock_socket = mock.Mock()
        mock_socket.send_to = ''
        try:
            utils.systemd_status(address, mock_socket, status, completed=True)
        except Exception:
            assert False, 'Exception was caught when should not have'

    def test_systemd_status_socket_error(self):
        address = 'address'
        status = 'Test'
        try:
            with mock.patch('novaagent.utils.socket') as test:
                test.sendto.side_effect = socket.error
                utils.systemd_status(address, test, status, completed=True)
        except socket_error:
            # This is the correct error to raise
            pass
        except Exception:
            assert False, 'Exception was caught when should not have'
