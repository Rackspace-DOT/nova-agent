
from __future__ import absolute_import


import logging
import time


from subprocess import PIPE
from subprocess import Popen


from novaagent import utils
from novaagent.libs import DefaultOS


log = logging.getLogger(__name__)


class ServerOS(DefaultOS):
    def __init__(self):
        super(ServerOS, self).__init__()
        self.netconfig_file = '/etc/network/interfaces'

    def _setup_loopback(self):
        with open(self.netconfig_file, 'w') as iffile:
            iffile.write('# The loopback network interface\n')
            iffile.write('auto lo\n')
            iffile.write('iface lo inet loopback\n\n')

    def _setup_interfaces(self, ifname, iface):
        with open(self.netconfig_file, 'a') as iffile:
            iffile.write('# Label {0}\n'.format(iface['label']))
            for count, x in enumerate(iface['ips']):
                if count == 0:
                    iffile.write('\nauto {0}\n'.format(ifname))
                    iffile.write('iface {0} inet static\n'.format(ifname))
                    iffile.write('\taddress {0}\n'.format(x['ip']))
                    iffile.write('\tnetmask {0}\n'.format(x['netmask']))
                    if iface.get('gateway'):
                        iffile.write(
                            '\tgateway {0}\n'.format(
                                iface['gateway']
                            )
                        )

                    if iface.get('dns'):
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

            if iface.get('ip6s'):
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
        hostname_return_code, _ = self._setup_hostname(client)
        if hostname_return_code != 0:
            log.error('Error setting hostname on system')

        xen_macs = utils.list_xenstore_macaddrs(client)
        for iface in utils.list_hw_interfaces():
            mac = utils.get_hw_addr(iface)
            if not mac or mac not in xen_macs:
                continue

            ifaces[iface] = utils.get_interface(mac, client)

        # Backup original configuration file
        utils.backup_file(self.netconfig_file)

        # Setup interfaces file
        self._setup_loopback()
        for ifname, iface in ifaces.items():
            self._setup_interfaces(ifname, iface)

        # Loop through the interfaces and restart networking
        for ifname in ifaces.keys():
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

            """
            In some cases interfaces may retain old IP addresses especially
            when building from a custom image. To prevent that we will do a
            flush of the interface before bringing it back up.

            Refer to bug:
            https://bugs.launchpad.net/ubuntu/+source/ifupdown/+bug/1584682
            """
            p = Popen(
                ['ip', 'addr', 'flush', 'dev', ifname],
                stdout=PIPE,
                stderr=PIPE,
                stdin=PIPE
            )
            out, err = p.communicate()
            if p.returncode != 0:
                return (
                    str(p.returncode),
                    'Error flushing network: {0}'.format(ifname)
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
                log.error(
                    'Error received on network restart: {0}'.format(err)
                )
                return (
                    str(p.returncode),
                    'Error starting network: {0}'.format(ifname)
                )

        return ('0', '')
