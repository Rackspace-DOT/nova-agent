from __future__ import print_function, absolute_import
from novaagent import utils
from novaagent.common.password import PasswordCommands
from subprocess import Popen, PIPE

from novaagent.libs import DefaultOS

class ServerOS(DefaultOS):
    def _setup_interface(ifname, iface):
        with open('/etc/rc.conf.local', 'a') as iffile:
            pass

    def resetnetwork(name, value):
        if os.path.exists('/etc/rc.conf.local'):
            os.rename('/etc/rc.conf.local', '/etc/rc.conf.local.bak')
        ifaces = {}
        xen_macs = utils.list_xenstore_macaddrs()
        for iface in utils.list_hw_interfaces():
            mac = utils.get_hw_addr(iface)
            if not mac or mac not in xen_macs:
                continue
            ifaces[iface] = utils.get_interface(mac)

        # set hostname
        hostname = utils.get_hostname()
        p = Popen(['hostname', hostname], stdout=PIPE, stdin=PIPE)
        out, err = p.communicate()
        if p.returncode != 0:
            return str(p.returncode)

        # setup interface files
        for ifname, iface in ifaces.items():
            _setup_interface(ifname, iface)
        p = Popen(['service', 'netif', 'restart'], stdout=PIPE, stdin=PIPE)
        p = Popen(['service', 'routing', 'restart'], stdout=PIPE, stdin=PIPE)
        out, err = p.communicate()
        if p.returncode != 0:
            return str(p.returncode)

        return '0'


if __name__ == '__main__':
    main()
