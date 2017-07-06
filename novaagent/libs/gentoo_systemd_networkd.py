from __future__ import print_function, absolute_import
import os

from novaagent import utils
from subprocess import Popen, PIPE

from novaagent.libs import DefaultOS


class ServerOS(DefaultOS):
    def _setup_interface(self, ifname, iface):
        addrs = []
        addrs.extend(['{0}/{1}'.format(x['ip'], utils.netmask_to_prefix(x['netmask'])) for x in iface['ips']])
        if 'ip6s' in iface and iface['ip6s']:
            addrs.extend(['{ip}/{netmask}'.format(**x) for x in iface['ip6s']])
        routes = []
        gateways = []
        if 'gateway' in iface and iface['gateway']:
            gateways.append(iface['gateway'])
        if 'gateway_v6' in iface and iface['gateway_v6']:
            gateways.append(iface['gateway_v6'])
        if 'routes' in iface and iface['routes']:
            for route in iface['routes']:
                route['length'] = utils.netmask_to_prefix(route['netmask'])
                routes.append(route)

        utils.backup_file('/etc/systemd/network/{0}.network'.format(ifname))
        with open('/etc/systemd/network/{0}.network'.format(ifname), 'w') as iffile:
            print('# Label {0}'.format(iface['label']), file=iffile)
            print('[Match]\nName={0}\n'.format(ifname), file=iffile)
            print('[Network]', file=iffile)
            for x in addrs:
                print('Address={0}'.format(x), file=iffile)
            for x in gateways:
                print('Gateway={0}'.format(x), file=iffile)
            if 'dns' in iface and iface['dns']:
                print('DNS={0}'.format(' '.join(iface['dns'])), file=iffile)
            for x in routes:
                print('\n[Route]\nGateway={gateway}\nDestination={route}/{length}'.format(**route), file=iffile)

    def resetnetwork(self, name, value):
        ifaces = {}
        xen_macs = utils.list_xenstore_macaddrs()
        for iface in utils.list_hw_interfaces():
            mac = utils.get_hw_addr(iface)
            if not mac or mac not in xen_macs:
                continue
            ifaces[iface] = utils.get_interface(mac)

        # set hostname
        utils.backup_file('/etc/hostname')
        hostname = utils.get_hostname()
        with open('/etc/hostname', 'w') as hostnamefile:
            print(hostname, file=hostnamefile)
        p = Popen(['hostname', hostname], stdout=PIPE, stderr=PIPE, stdin=PIPE)
        out, err = p.communicate()
        if p.returncode != 0:
            return (str(p.returncode), 'Error setting hostname: hostname')

        # setup interface files
        for ifname, iface in ifaces.items():
            self._setup_interface(ifname, iface)

        p = Popen(['/usr/bin/systemctl', 'restart', 'systemd-networkd'], stdout=PIPE, stderr=PIPE, stdin=PIPE)
        out, err = p.communicate()
        if p.returncode != 0:
            return (str(p.returncode), 'Error restarting network')

        return ('0', '')


if __name__ == '__main__':
    main()
