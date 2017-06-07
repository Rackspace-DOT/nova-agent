
from subprocess import PIPE, Popen

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


def backup_file(config):
    if not os.path.exists(config):
        return

    bakfile_suffix = '{0}.bak'.format(time.time())
    bakfile = '{0}.{1}'.format(config, bakfile_suffix)
    log.info('Backing up -> {0} ({1})'.format(config, bakfile_suffix))
    shutil.copyfile(config, bakfile)


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

    for filepath in glob.glob(net_config_dir + "/ifcfg-*"):
        if '.' not in filepath and filepath not in interfaces:
            remove_files.append(filepath)

    return remove_files


def get_interface(mac):
    p = Popen(
        'xenstore-read vm-data/networking/{0}'.format(mac),
        stdout=PIPE,
        stderr=PIPE,
        shell=True
    )
    out, err = p.communicate()
    if p.returncode == 0:
        ret = json.loads(out.decode('utf-8').strip())
        log.info('interface {0}: {1}'.format(mac, ret))
        return ret
    return False


def list_xenstore_macaddrs():
    p = Popen('xenstore-ls vm-data/networking', stdout=PIPE, shell=True)
    out, err = p.communicate()
    out = out.decode('utf-8').split('\n')
    out = [x.split(' = ')[0] for x in out if x]
    return out


def get_hw_addr(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        info = fcntl.ioctl(
            s.fileno(),
            0x8927,
            struct.pack('256s', bytes(ifname[:15]))
        )
        return ''.join(['%02x' % ord(char) for char in info[18:24]]).upper()
    except TypeError as exc:
        info = fcntl.ioctl(
            s.fileno(),
            0x8927,
            struct.pack('256s', bytes(ifname[:15], 'utf-8'))
        )
        return ''.join(['%02x' % char for char in info[18:24]]).upper()
    except IOError as exc:
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


def get_hostname():
    p = Popen(
        'xenstore-read vm-data/hostname',
        stdout=PIPE,
        stderr=PIPE,
        shell=True
    )
    out, err = p.communicate()
    xen_hostname = out.decode('utf-8').split('\n')[0]
    if p.returncode == 0:
        ret = xen_hostname
    else:
        ret = socket.gethostname()
    log.info('hostname: {0}'.format(ret))
    return ret


def list_xen_events():
    p = Popen('xenstore-ls data/host', stdout=PIPE, stderr=PIPE, shell=True)
    out, err = p.communicate()
    out = out.decode('utf-8').split('\n')
    out = [x.split(' = ')[0] for x in out if x]
    return out


def get_xen_event(uuid):
    p = Popen(
        'xenstore-read data/host/{0}'.format(uuid),
        stdout=PIPE,
        stderr=PIPE,
        shell=True
    )
    out, err = p.communicate()
    ret = json.loads(out.decode('utf-8').strip())
    return ret


def remove_xenhost_event(uuid):
    p = Popen(
        'xenstore-rm data/host/{0}'.format(uuid),
        stdout=PIPE,
        stderr=PIPE,
        shell=True
    )
    out, err = p.communicate()
    if p.returncode == 0:
        return True
    return False


def update_xenguest_event(uuid, data):
    p = Popen(
        'xenstore-write data/guest/{0} \'{1}\''.format(uuid, json.dumps(data)),
        stdout=PIPE,
        stderr=PIPE,
        shell=True
    )
    out, err = p.communicate()
    if p.returncode == 0:
        return True
    return False
