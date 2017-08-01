from __future__ import print_function, absolute_import


import time
import os


from novaagent import utils
from subprocess import Popen, PIPE
from novaagent.libs import DefaultOS


class ServerOS(DefaultOS):
    def __init__(self):
        self.netconfig_file = '/etc/network/interfaces'
        self.hostname_file = '/etc/hostname'

    def _setup_loopback(self):
        utils.backup_file(self.netconfig_file)
        with open(self.netconfig_file, 'w') as iffile:
            iffile.write('# The loopback network interface\n')
            iffile.write('auto lo\n')
            iffile.write('iface lo inet loopback\n\n')

    def _setup_hostname(self, client):
        """
        hostnamectl is available in some Debian systems and depends on dbus
        """
        hostname = utils.get_hostname(client)
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

    def _setup_interface(self, ifname, iface):
        with open(self.netconfig_file, 'a') as iffile:
            iffile.write('# Label {0}\n'.format(iface['label']))
            for count, x in enumerate(iface['ips']):
                if count == 0:
                    iffile.write('\nauto {0}\n'.format(ifname))
                    iffile.write('iface {0} inet static\n'.format(ifname))
                    iffile.write('\taddress {0}\n'.format(x['ip']))
                    iffile.write('\tnetmask {0}\n'.format(x['netmask']))
                    if 'gateway' in iface and iface['gateway']:
                        iffile.write(
                            '\tgateway {0}\n'.format(
                                iface['gateway']
                            )
                        )

                    if 'dns' in iface and iface['dns']:
                        iffile.write(
                            '\tdns-nameservers {0}\n'.format(
                                ' '.join(iface['dns'])
                            )
                        )

                    if 'routes' in iface:
                        for route in iface['routes']:
                            iffile.write(
                                '\tpost-up route add -net {0} netmask '
                                '{1} gw {2} || true\n'.format(
                                    route['route'],
                                    route['netmask'],
                                    route['gateway']
                                )
                            )
                            iffile.write(
                                '\tpost-down route add -net {0} netmask '
                                '{1} gw {2} || true\n'.format(
                                    route['route'],
                                    route['netmask'],
                                    route['gateway']
                                )
                            )

                else:
                    iffile.write('\nauto {0}:{1}\n'.format(ifname, count))
                    iffile.write(
                        'iface {0}:{1} inet static\n'.format(
                            ifname,
                            count
                        )
                    )
                    iffile.write('\taddress {0}\n'.format(x['ip']))
                    iffile.write('\tnetmask {0}\n'.format(x['netmask']))

            if 'ip6s' in iface and iface['ip6s']:
                for count, ip_info in enumerate(iface['ip6s']):
                    if count == 0:
                        iffile.write(
                            '\niface {0} inet6 static\n'.format(ifname)
                        )
                        iffile.write('\taddress {0}\n'.format(ip_info['ip']))
                        iffile.write(
                            '\tnetmask {0}\n'.format(
                                ip_info['netmask']
                            )
                        )

                        if 'gateway_v6' in iface and iface['gateway_v6']:
                            iffile.write(
                                '\tgateway {0}\n'.format(
                                    iface['gateway_v6']
                                )
                            )

                    else:
                        iffile.write(
                            '\niface {0}:{1} inet6 static\n'.format(
                                ifname,
                                count
                            )
                        )
                        iffile.write('\taddress {0}'.format(ip_info['ip']))
                        iffile.write(
                            '\tnetmask {0}\n'.format(
                                ip_info['netmask']
                            )
                        )

            iffile.write('\n')

    def resetnetwork(self, name, value, client):
        ifaces = {}
        hostname_return_code, hostname = self._setup_hostname(client)
        if hostname_return_code != 0:
            return (str(hostname_return_code), 'Error setting hostname')

        xen_macs = utils.list_xenstore_macaddrs(client)
        for iface in utils.list_hw_interfaces():
            mac = utils.get_hw_addr(iface)
            if not mac or mac not in xen_macs:
                continue

            ifaces[iface] = utils.get_interface(mac, client)

        # setup interface files
        self._setup_loopback()
        for ifname, iface in ifaces.items():
            self._setup_interface(ifname, iface)
            p = Popen(
                ['ifdown', ifname],
                stdout=PIPE,
                stderr=PIPE,
                stdin=PIPE
            )
            out, err = p.communicate()
            if p.returncode != 0:
                return (
                    str(p.returncode),
                    'Error stopping network: {0}'.format(ifname)
                )

            # Sleep for one second
            time.sleep(1)
            p = Popen(
                ['ifup', ifname],
                stdout=PIPE,
                stderr=PIPE,
                stdin=PIPE
            )
            out, err = p.communicate()
            if p.returncode != 0:
                return (
                    str(p.returncode),
                    'Error starting network: {0}'.format(ifname)
                )

        return ('0', '')
