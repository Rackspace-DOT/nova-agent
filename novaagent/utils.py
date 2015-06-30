from subprocess import PIPE, Popen
import fcntl, socket, struct
import os
import json

try:
    import netifaces
    HAS_NETIFACES = True
except ImportError as exc:
    HAS_NETIFACES = False


def get_interface(mac):
    p = Popen(['xenstore-read', 'vm-data/networking/{0}'.format(mac)], stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if p.returncode == 0:
        return json.loads(out.decode('utf-8').strip())
    return False


def list_xenstore_macaddrs():
    p = Popen(['xenstore-ls', 'vm-data/networking'], stdout=PIPE)
    out, err = p.communicate()
    out = out.decode('utf-8').split('\n')
    out = [x.split(' = ')[0] for x in out if x]
    return out


def get_hw_addr(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', bytes(ifname[:15])))
        return ''.join(['%02x' % ord(char) for char in info[18:24]]).upper()
    except TypeError as exc:
        info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', bytes(ifname[:15], 'utf-8')))
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
    p = Popen(['xenstore-read', 'vm-data/hostname'], stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    xen_hostname = out.decode('utf-8').split('\n')[0]
    if p.returncode == 0:
        return xen_hostname
    return socket.gethostname()


def list_xen_events():
    p = Popen(['xenstore-ls', 'data/host'], stdout=PIPE)
    out, err = p.communicate()
    out = out.decode('utf-8').split('\n')
    out = [x.split(' = ')[0] for x in out if x]
    return out


def get_xen_event(uuid):
    p = Popen(['xenstore-read', 'data/host/{0}'.format(uuid)], stdout=PIPE)
    out, err = p.communicate()
    ret = json.loads(out.decode('utf-8').strip())
    return ret


def remove_xenhost_event(uuid):
    p = Popen(['xenstore-rm', 'data/host/{0}'.format(uuid)], stdout=PIPE)
    out, err = p.communicate()
    if p.returncode == 0:
        return True
    return False


def update_xenguest_event(uuid, data):
    p = Popen(['xenstore-write', 'data/guest/{0}'.format(uuid), json.dumps(data)], stdout=PIPE)
    out, err = p.communicate()
    if p.returncode == 0:
        return True
    return False
