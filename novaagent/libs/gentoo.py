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
        if 'gateway' in iface and iface['gateway']:
            routes.append('default via {0}'.format(iface['gateway']))
        if 'gateway_v6' in iface and iface['gateway_v6']:
            routes.append('default via {0}'.format(iface['gateway_v6']))
        if 'routes' in iface and iface['routes']:
            for route in iface['routes']:
                routes.append('{route}/{netmask} via {gateway}'.format(**route))

        with open('/etc/conf.d/net', 'a') as iffile:
            print('# Label {0}'.format(iface['label']), file=iffile)
            print('config_{0}="\n\t{1}\n"'.format(ifname, '\n\t'.join(addrs)), file=iffile)
            print('routes_{0}="\n\t{1}\n"'.format(ifname, '\n\t'.join(routes)), file=iffile)
            if 'dns' in iface and iface['dns']:
                print('dns_servers_{0}="\n\t{1}\n"'.format(ifname, '\n\t'.join(iface['dns'])), file=iffile)

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
        utils.backup_file('/etc/conf.d/hostname')
        hostname = utils.get_hostname()
        with open('/etc/hostname', 'w') as hostnamefile:
            print(hostname, file=hostnamefile)
        with open('/etc/conf.d/hostname', 'w') as hostnamefile:
            print('HOSTNAME={0}'.format(hostname), file=hostnamefile)
        p = Popen(['hostname', hostname], stdout=PIPE, stderr=PIPE, stdin=PIPE)
        out, err = p.communicate()
        if p.returncode != 0:
            return (str(p.returncode), 'Error setting hostname: hostname')

        # setup interface files
        utils.backup_file('/etc/conf.d/net')
        with open('/etc/conf.d/net', 'w') as iffile:
            print('modules="iproute2"', file=iffile)
        for ifname, iface in ifaces.items():
            self._setup_interface(ifname, iface)
            p = Popen(['/etc/init.d/net.{0}'.format(ifname), 'restart'], stdout=PIPE, stderr=PIPE, stdin=PIPE)
            out, err = p.communicate()
            if p.returncode != 0:
                return (str(p.returncode), 'Error restarting network')

        return ('0', '')


if __name__ == '__main__':
    main()
