from __future__ import print_function, absolute_import
import os

from novaagent import utils
from subprocess import Popen, PIPE

from novaagent.libs import DefaultOS


class ServerOS(DefaultOS):
    def _setup_loopback(self):
        with open('/etc/network/interfaces', 'w') as iffile:
            print((
                '# The loopback network interface\n'
                'auto lo\n'
                'iface lo inet loopback\n\n'
            ), file=iffile)

    def _setup_interface(self, ifname, iface):
        with open('/etc/network/interfaces', 'a') as iffile:
            print('# Label {0}'.format(iface['label']), file=iffile)
            for count, x in enumerate(iface['ips']):
                if count == 0:
                    print('auto {0}'.format(ifname), file=iffile)
                    print('iface {0} inet static'.format(ifname), file=iffile)
                    print('\taddress {0}'.format(x['ip']), file=iffile)
                    print('\tnetmask {0}'.format(x['netmask']), file=iffile)
                    if 'gateway' in iface and iface['gateway']:
                        print('\tgateway {0}'.format(iface['gateway']), file=iffile)
                    if 'dns' in iface and iface['dns']:
                        print("\tdns-nameservers {0}".format(' '.join(dns)), file=iffile)
                    if 'routes' in iface:
                        for route in iface['routes']:
                            print((
                                '\tpost-up route add -net {route} netmask {netmask} gw {gateway} || true'
                                '\tpost-down route add -net {route} netmask {netmask} gw {gateway} || true'
                            ).format(**route), file=iffile)
                else:
                    print('auto {0}:{1}'.format(ifname, count), file=iffile)
                    print('iface {0}:{1} inet static'.format(ifname, count), file=iffile)
                    print('\taddress {0}'.format(x['ip']), file=iffile)
                    print('\tnetmask {0}'.format(x['netmask']), file=iffile)
            if 'ip6s' in iface and iface['ip6s']:
                for count, x in enumerate(iface['ip6s']):
                    if count == 0:
                        print('auto {0}'.format(ifname), file=iffile)
                        print('iface {0} inet6 static'.format(ifname), file=iffile)
                        print('\taddress {0}'.format(x['ip']), file=iffile)
                        print('\tnetmask {0}'.format(x['netmask']), file=iffile)
                        if 'gateway' in iface and iface['gateway']:
                            print('\tgateway {0}'.format(iface['gateway']), file=iffile)
                    else:
                        print('auto {0}:{1}'.format(ifname, count), file=iffile)
                        print('iface {0}:{1} inet6 static'.format(ifname, count), file=iffile)
                        print('\taddress {0}'.format(x['ip']), file=iffile)
                        print('\tnetmask {0}'.format(x['netmask']), file=iffile)

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
        with open('/etc/hostname', 'w') as hostnamefile:
            print(hostname, file=hostnamefile)
        if os.path.exists('/usr/bin/hostnamectl'):
            p = Popen(['hostnamectl', 'set-hostname', hostname], stdout=PIPE, stderr=PIPE, stdin=PIPE)
            out, err = p.communicate()
            if p.returncode != 0:
                return (str(p.returncode), 'Error setting hostname')
        else:
            p = Popen(['hostname', hostname], stdout=PIPE, stderr=PIPE, stdin=PIPE)
            out, err = p.communicate()
            if p.returncode != 0:
                return (str(p.returncode), 'Error setting hostname')

        # setup interface files
        for ifname, iface in ifaces.items():
            self._setup_loopback()
            self._setup_interface(ifname, iface)
        p = Popen(['service', 'networking', 'restart'], stdout=PIPE, stderr=PIPE, stdin=PIPE)
        out, err = p.communicate()
        if p.returncode != 0:
            return (str(p.returncode), 'Error restarting network')

        return ('0', '')


if __name__ == '__main__':
    main()
