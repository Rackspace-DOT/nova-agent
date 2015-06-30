from __future__ import print_function, absolute_import
from novaagent import utils
from novaagent.common.password import PasswordCommands
from subprocess import Popen, PIPE

from novaagent.libs import DefaultOS


class ServerOS(DefaultOS):
    def _setup_interface(self, ifname, iface):
        with open('/etc/netctl/{0}'.format(ifname), 'w') as iffile:
            print('# Label {0}'.format(iface['label']), file=iffile)
            print('Connection=ethernet', file=iffile)
            print('Interface={0}'.format(ifname), file=iffile)
            print('IP=static', file=iffile)
            addrs = ['{0}/{1}'.format(x['ip'], x['netmask']) for x in iface['ips']]
            print("Address=('{0}')".format("' '".join(addrs)), file=iffile)
            if 'gateway' in iface and iface['gateway']:
                print('Gateway={0}'.format(iface['gateway']), file=iffile)
            if 'routes' in iface and iface['routes']:
                routes = ['{route}/{netmask} via {gateway}'.format(**x) for x in iface['routes']]
                print("Routes=('{0}')".format("' '".join(routes)), file=iffile)
            if 'ip6s' in iface and iface['ip6s']:
                print('IP6=static', file=iffile)
                addrs6 = ['{0}/{1}'.format(x['ip'], x['netmask']) for x in iface['ip6s']]
                print("Address6=('{0}')".format("' '".join(addrs6)), file=iffile)
                print('Gateway6={0}'.format(iface['gateway_v6']), file=iffile)
            if 'dns' in iface and iface['dns']:
                print("DNS=('{0}')".format("' '".join(iface['dns'])), file=iffile)

    def resetnetwork(self, name, value):
        ifaces = {}
        xen_macs = utils.list_xenstore_macaddrs()
        for iface in utils.list_hw_interfaces():
            mac = utils.get_hw_addr(iface)
            if not mac or mac not in xen_macs:
                continue
            ifaces[iface] = utils.get_interface(mac)

        # set hostname
        hostname = utils.get_hostname()
        p = Popen(['hostnamectl', 'set-hostname', hostname], stdout=PIPE, stderr=PIPE, stdin=PIPE)
        out, err = p.communicate()
        if p.returncode != 0:
            return str(p.returncode)

        # setup interface files
        for ifname, iface in ifaces.items():
            self._setup_interface(ifname, iface)
            p = Popen(['netctl', 'restart', ifname], stdout=PIPE, stderr=PIPE, stdin=PIPE)
            out, err = p.communicate()
            if p.returncode != 0:
                return str(p.returncode)

        return '0'


if __name__ == '__main__':
    main()
