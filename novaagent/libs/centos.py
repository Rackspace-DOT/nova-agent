from __future__ import print_function, absolute_import

import os

from novaagent import utils
from subprocess import Popen, PIPE
from novaagent.libs import DefaultOS


class ServerOS(DefaultOS):
    def __init__(self):
        self.netconfig_dir = '/etc/sysconfig/network-scripts'
        self.interface_file_prefix = 'ifcfg'
        self.route_file_prefix = 'route'
        self.hostname_file = '/etc/hostname'
        self.network_file = '/etc/sysconfig/network'

    def _setup_interface(self, ifname, iface):
        interface_file = '{0}/{1}-{2}'.format(
            self.netconfig_dir,
            self.interface_file_prefix,
            ifname
        )
        utils.backup_file(interface_file)
        with open(interface_file, 'w') as iffile:
            iffile.write('# Label {0}\n'.format(iface['label']))
            iffile.write('BOOTPROTO=static\n')
            iffile.write('DEVICE={0}\n'.format(ifname))
            for count, ip_info in enumerate(iface['ips']):
                if count == 0:
                    iffile.write('IPADDR={0}\n'.format(ip_info['ip']))
                    iffile.write('NETMASK={0}\n'.format(ip_info['netmask']))
                else:
                    iffile.write(
                        'IPADDR{0}={1}\n'.format(
                            count,
                            ip_info['ip']
                        )
                    )
                    iffile.write(
                        'NETMASK{0}={1}\n'.format(
                            count,
                            ip_info['netmask']
                        )
                    )

            if 'gateway' in iface and iface['gateway']:
                iffile.write('GATEWAY={0}\n'.format(iface['gateway']))

            if 'ip6s' in iface and iface['ip6s']:
                iffile.write('IPV6INIT=yes\n')
                for count, ip6_info in enumerate(iface['ip6s']):
                    if count == 0:
                        iffile.write(
                            'IPV6ADDR={0}/{1}\n'.format(
                                ip6_info['ip'],
                                ip6_info['netmask']
                            )
                        )
                    else:
                        iffile.write(
                            'IPV6ADDR{0}={1}/{2}\n'.format(
                                count,
                                ip6_info['ip'],
                                ip6_info['netmask']
                            )
                        )

                iffile.write(
                    'IPV6_DEFAULTGW={0}%{1}\n'.format(
                        iface['gateway_v6'],
                        ifname
                    )
                )

            if 'dns' in iface and iface['dns']:
                for count, dns in enumerate(iface['dns']):
                    iffile.write('DNS{0}={1}\n'.format(count + 1, dns))

            iffile.write('ONBOOT=yes\n')
            iffile.write('NM_CONTROLLED=no\n')

    def _setup_routes(self, ifname, iface):
        route_file = '{0}/{1}-{2}'.format(
            self.netconfig_dir,
            self.route_file_prefix,
            ifname
        )
        utils.backup_file(route_file)
        with open(route_file, 'w') as routefile:
            for count, route in enumerate(iface['routes']):
                routefile.write(
                    'ADDRESS{0}={1}\n'.format(
                        count,
                        route['route']
                    )
                )
                routefile.write(
                    'NETMASK{0}={1}\n'.format(
                        count,
                        route['netmask']
                    )
                )
                routefile.write(
                    'GATEWAY{0}={1}\n'.format(
                        count,
                        route['gateway']
                    )
                )

    def _setup_hostname(self):
        hostname = utils.get_hostname()
        if os.path.exists('/usr/bin/hostnamectl'):
            utils.backup_file(self.hostname_file)
            p = Popen(
                ['hostnamectl', 'set-hostname', hostname],
                stdout=PIPE,
                stderr=PIPE,
                stdin=PIPE
            )
            out, err = p.communicate()
        else:
            p = Popen(
                ['hostname', hostname],
                stdout=PIPE,
                stderr=PIPE,
                stdin=PIPE
            )
            out, err = p.communicate()

        return p.returncode, hostname

    def resetnetwork(self, name, value):
        ifaces = {}
        hostname_return_code, hostname = self._setup_hostname()
        if hostname_return_code != 0:
            return (str(hostname_return_code), 'Error setting hostname')

        xen_macs = utils.list_xenstore_macaddrs()
        for iface in utils.list_hw_interfaces():
            mac = utils.get_hw_addr(iface)

            if not mac or mac not in xen_macs:
                continue

            ifaces[iface] = utils.get_interface(mac)

        utils.backup_file(self.network_file)
        with open(self.network_file, 'w') as netfile:
            netfile.write('NETWORKING=yes\n')
            netfile.write('NOZEROCONF=yes\n')
            netfile.write('NETWORKING_IPV6=yes\n')
            netfile.write('HOSTNAME={0}\n'.format(hostname))

        # move unused interface files out of the way but back them up
        move_files = utils.get_ifcfg_files_to_remove(
            self.netconfig_dir,
            '{0}-'.format(self.interface_file_prefix)
        )
        for interface_config in move_files:
            utils.move_file(interface_config)

        # setup interface files
        for ifname, iface in ifaces.items():
            self._setup_interface(ifname, iface)
            if 'routes' in iface:
                self._setup_routes(ifname, iface)

        p = Popen(
            ['service', 'network', 'stop'],
            stdout=PIPE,
            stderr=PIPE,
            stdin=PIPE
        )
        p = Popen(
            ['service', 'network', 'start'],
            stdout=PIPE,
            stderr=PIPE,
            stdin=PIPE
        )
        out, err = p.communicate()
        if p.returncode != 0:
            return (str(p.returncode), 'Error restarting network')

        return ('0', '')
