
import fcntl
import socket
import struct
import os
import shutil
import json
import time
import glob
import logging


log = logging.getLogger(__name__)


try:
    import netifaces
    HAS_NETIFACES = True
except ImportError as exc:
    HAS_NETIFACES = False


# Why is this function and move_file both here as they do the same thing
def backup_file(config):
    if not os.path.exists(config):
        return

    bakfile_suffix = '{0}.bak'.format(time.time())
    bakfile = '{0}.{1}'.format(config, bakfile_suffix)
    log.info('Backing up -> {0} ({1})'.format(config, bakfile_suffix))
    shutil.copyfile(config, bakfile)


def encode_to_bytes(data_string):
    try:
        return bytes(data_string)
    except:
        return bytes(data_string, 'utf-8')


def netmask_to_prefix(netmask):
    return sum([bin(int(x)).count('1') for x in netmask.split('.')])


def move_file(interface_config):
    if not os.path.exists(interface_config):
        return

    bakfile_suffix = '{0}.bak'.format(time.time())
    log.info('Moving {0} -> {0}.{1}'.format(interface_config, bakfile_suffix))
    os.rename(
        interface_config, '{0}.{1}'.format(
            interface_config,
            bakfile_suffix
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
        return ''.join(['%02x' % ord(char) for char in info[18:24]]).upper()
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
    get_interface = encode_to_bytes(
        'vm-data/networking/{0}'.format(mac_address)
    )
    try:
        interface = json.loads(
            client.read(get_interface).decode('utf-8').strip()
        )
    except:
        pass

    log.info('interface {0}: {1}'.format(mac_address, interface))
    return interface


def list_xenstore_macaddrs(client):
    mac_addrs = []
    try:
        for item in client.list(b'vm-data/networking'):
            mac_addrs.append(item.decode('utf-8').strip())
    except:
        pass

    return mac_addrs


def get_hostname(client):
    xen_hostname = None
    try:
        xen_hostname = client.read(b'vm-data/hostname').decode('utf-8').strip()
    except:
        xen_hostname = socket.gethostname()

    log.info('hostname: {0}'.format(xen_hostname))
    return xen_hostname


def list_xen_events(client):
    message_uuids = []
    try:
        for item in client.list(b'data/host'):
            message_uuids.append(item.decode('utf-8').strip())
    except:
        pass

    return message_uuids


def get_xen_event(uuid, client):
    event_detail = None
    get_xen_event = encode_to_bytes('data/host/{0}'.format(uuid))
    try:
        event_detail = json.loads(
            client.read(get_xen_event).decode('utf-8').strip()
        )
    except:
        pass

    return event_detail


def remove_xenhost_event(uuid, client):
    success = False
    remove_xen_event = encode_to_bytes('data/host/{0}'.format(uuid))
    try:
        client.delete(remove_xen_event)
        success = True
    except:
        pass

    return success


def update_xenguest_event(uuid, data, client):
    success = False
    write_path = encode_to_bytes('data/guest/{0}'.format(uuid))
    write_value = encode_to_bytes(json.dumps(data))

    try:
        client.write(write_path, write_value)
        success = True
    except:
        pass

    return success
