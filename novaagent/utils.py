
from __future__ import absolute_import


from socket import error as socket_error


from novaagent.xenstore import xenstore


import logging
import socket
import signal
import struct
import fcntl
import json
import time
import glob
import os


log = logging.getLogger(__name__)


try:
    import netifaces
    HAS_NETIFACES = True
except ImportError as exc:
    HAS_NETIFACES = False


def encode_to_bytes(data_string):
    try:
        return bytes(data_string)
    except Exception:
        return bytes(data_string, 'utf-8')


def netmask_to_prefix(netmask):
    return sum([bin(int(x)).count('1') for x in netmask.split('.')])


def backup_file(backup_file):
    if not os.path.exists(backup_file):
        return

    backup_file_suffix = '{0}.bak'.format(time.time())
    log.info('Backing up -> {0} ({1})'.format(backup_file, backup_file_suffix))
    os.rename(
        backup_file, '{0}.{1}'.format(
            backup_file,
            backup_file_suffix
        )
    )


def get_ifcfg_files_to_remove(net_config_dir, interface_file_prefix):
    interfaces = []
    remove_files = []
    for iface in os.listdir('/sys/class/net/'):
        interfaces.append(net_config_dir + '/' + interface_file_prefix + iface)

    for filepath in glob.glob(
        net_config_dir + '/{0}*'.format(interface_file_prefix)
    ):
        if '.' not in filepath and filepath not in interfaces:
            remove_files.append(filepath)

    return remove_files


def get_provider(client=None):
    provider = None
    try:
        provider_path = encode_to_bytes('vm-data/provider_data/provider')
        provider = xenstore.xenstore_read(provider_path, client)
    except Exception as e:
        log.error(
            'Exception occurred trying to get provider: {0}'.format(str(e))
        )

    log.info('Provider: {0}'.format(provider))
    return provider


def get_hw_addr(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        bin_ifname = bytes(ifname[:15])
    except TypeError:
        bin_ifname = bytes(ifname[:15], 'utf-8')

    try:
        info = fcntl.ioctl(
            s.fileno(),
            0x8927,
            struct.pack('256s', bin_ifname)
        )
        try:
            hw_address = ''.join(
                ['%02x' % ord(char) for char in info[18:24]]
            ).upper()
        except Exception:
            hw_address = ''.join(
                ['%02x' % char for char in info[18:24]]
            ).upper()

        return hw_address
    except IOError:
        if HAS_NETIFACES is False:
            return False

        iface = netifaces.ifaddresses(ifname)
        if netifaces.AF_LINK in iface:
            mac = iface[netifaces.AF_LINK][0]['addr']
            return mac.replace(':', '').upper()

        return False


def list_hw_interfaces():
    if os.path.exists('/sys/class/net'):
        return os.listdir('/sys/class/net')

    return netifaces.interfaces()


def get_interface(mac_address, client):
    interface = None
    try:
        get_interface = encode_to_bytes(
            'vm-data/networking/{0}'.format(mac_address)
        )
        interface = json.loads(
            xenstore.xenstore_read(get_interface, client)
        )
    except Exception as e:
        log.error(
            'Exception was caught getting the interface: {0}'.format(str(e))
        )

    log.info('Interface {0}: {1}'.format(mac_address, interface))
    return interface


def list_xenstore_macaddrs(client):
    mac_addrs = []
    try:
        mac_addrs = xenstore.xenstore_list(b'vm-data/networking', client)
    except Exception as e:
        log.error('Exception was caught getting mac addrs: {0}'.format(str(e)))

    return mac_addrs


def get_hostname(client):
    xen_hostname = None
    try:
        xen_hostname = xenstore.xenstore_read(b'vm-data/hostname', client)
        if xen_hostname is None:
            raise ValueError('Shell to xenstore-read for hostname failed')
    except Exception:
        xen_hostname = socket.gethostname()

    log.info('Hostname: {0}'.format(xen_hostname))
    return xen_hostname


def list_xen_events(client):
    """
        After a reboot it is possible that the data/host path is not present.
        Once an action is passed to the instance then the path will be
        created and this will not generate an exception.

        Changing the log level to debug from error and making a better log
        message
    """
    message_uuids = []
    try:
        message_uuids = xenstore.xenstore_list(b'data/host', client)
    except Exception as e:
        log.debug(
            'Exception reading data/host: {0}'.format(str(e))
        )

    return message_uuids


def get_xen_event(uuid, client):
    event_detail = None
    get_xen_event = encode_to_bytes('data/host/{0}'.format(uuid))
    try:
        event_detail = xenstore.xenstore_read(get_xen_event, client, True)
    except Exception as e:
        log.error(
            'Exception was caught reading xen event: {0}'.format(str(e))
        )

    return event_detail


def remove_xenhost_event(uuid, client):
    success = False
    remove_xen_event = encode_to_bytes('data/host/{0}'.format(uuid))
    try:
        xenstore.xenstore_delete(remove_xen_event, client)
        success = True
    except Exception as e:
        log.error(
            'Exception was caught removing xen event: {0}'.format(str(e))
        )

    return success


def update_xenguest_event(uuid, data, client):
    success = False
    write_path = encode_to_bytes('data/guest/{0}'.format(uuid))
    write_value = encode_to_bytes(json.dumps(data))
    try:
        xenstore.xenstore_write(write_path, write_value, client)
        success = True
    except Exception as e:
        log.error(
            'Exception was caught writing xen event: {0}'.format(str(e))
        )

    return success


def send_notification(server_init, notify):
    # Only need to notify systemd and upstart init systems
    if server_init == 'systemd':
        systemd_status(*notify, status='', completed=True)
    elif server_init == 'upstart':
        os.kill(os.getpid(), signal.SIGSTOP)


def notify_socket():
    """Return a tuple of address, socket for future use"""
    _empty = None, None
    address = os.environ.pop("NOTIFY_SOCKET", None)

    if not address:
        return _empty

    if len(address) == 1:
        return _empty

    if address[0] not in ("@", "/"):
        return _empty

    if address[0] == "@":
        address = "\0" + address[1:]

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    return address, sock


def systemd_status(address, sock, status, completed=False):
    """Helper function to update the service status."""
    if completed:
        message = b"READY=1"
    else:
        message = ("STATUS={0}".format(status)).encode('utf8')

    if not (address and sock and message):
        return

    try:
        sock.sendto(message, address)
    except socket_error as serr:
        log.error('Socket error occurred on message send')
        raise serr

    return
