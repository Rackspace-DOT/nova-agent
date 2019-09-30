from __future__ import absolute_import

import logging
import os
import re

import distro
from subprocess import Popen
from subprocess import PIPE

from novaagent import utils
from novaagent.libs import DefaultOS

log = logging.getLogger(__name__)


class ServerOS(DefaultOS):
    def __init__(self):
        super(ServerOS, self).__init__()
        self.netconfig_dir = '/etc/sysconfig/network-scripts'
        self.network_file = '/etc/sysconfig/network'
        self.interface_file_prefix = 'ifcfg'
        self.route_file_prefix = 'route'
        self.use_network_manager = self.is_network_manager()

    def _setup_interface(self, ifname, iface):
        interface_file = '{0}/{1}-{2}'.format(
            self.netconfig_dir,
            self.interface_file_prefix,
            ifname
        )
        # Check and see if there are extra arguments in ifcfg file
        extra_args = self._check_for_extra_settings(interface_file)

        # Backup the interface file
        utils.backup_file(interface_file)

        with open(interface_file, 'w') as iffile:
            iffile.write('# Automatically generated, do not edit\n\n')
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

            if iface.get('gateway'):
                iffile.write('GATEWAY={0}\n'.format(iface['gateway']))

            if iface.get('ip6s'):
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

            if iface.get('dns'):
                for count, dns in enumerate(iface['dns']):
                    iffile.write('DNS{0}={1}\n'.format(count + 1, dns))

            iffile.write('ONBOOT=yes\n')
            if not self.use_network_manager:
                iffile.write('NM_CONTROLLED=no\n')

            if len(extra_args) > 0:
                for argument in extra_args:
                    iffile.write('{0}\n'.format(argument))

    def _check_for_extra_settings(self, interface_file):
        add_args = []

        # The below setting are set in _setup_interface and also ignoring lines
        # that start with # (comments) and lines with spaces at the beginning
        known_settings = [  # noqa
            '^BOOTPROTO=', '^DEVICE=', '^GATEWAY=', '^IPV6INIT=', '^IPV6ADDR=',
            '^IPV6_DEFAULTGW=', '^ONBOOT=', '^NM_CONTROLLED=', '^HWADDR=',
            '^DNS\d+?=', '^IPADDR\d?', '^NETMASK\d?', '^#', '^\s+'
        ]
        log.debug('Checking for additional arguments for ifcfg')
        pattern = re.compile('|'.join(known_settings))

        # File will not exist on initial boot so check and make sure exists
        if os.path.isfile(interface_file):
            with open(interface_file, 'r') as file:
                for line in file:
                    if not pattern.search(line):
                        add_args.append(line.strip())

        log.debug(
            'Found {0} extra arguments to '
            'add to ifcfg file'.format(len(add_args))
        )
        return add_args

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

    @staticmethod
    def version_float():
        """Float of os version major.minor"""
        version = "{0}.{1}".format(distro.major_version(),
                                   distro.minor_version())
        return float(version)

    @staticmethod
    def _os_defaults_network_manager():
        """
        :rtype: bool
        :return: has network manager only, not network scripts
        """
        dist = distro.id()
        server_os_version = ServerOS.version_float()

        log.info("Linux Distribution Detected: {0} Version {1}".format(
            dist, ServerOS.version_float()))
        if dist == 'rhel' and server_os_version >= 8:
            return True

        if dist == 'centos' and server_os_version >= 8:
            return True

        if dist == 'fedora' and server_os_version >= 29:
            return True

        return False

    def is_network_manager(self):
        """ Is using NetworkManager over network scripts

        :rtype: bool
        :return: OS Defaults to network manager
        """
        result = False

        if not self._os_defaults_network_manager():
            return False

        try:
            p = Popen(
                ['systemctl', 'is-enabled', 'NetworkManager.service'],
                stdout=PIPE,
                stderr=PIPE,
                stdin=PIPE
            )
            out, err = p.communicate()
            if p.returncode != 0:
                return False
            if 'enabled'.encode() in out:
                result = True
        except Exception as e:
            log.info(
                'Error checking if NetworkManager is enabled {0}'.format(e))
            log.info('Falling back to service network restart')

        return result

    def resetnetwork(self, name, value, client):
        ifaces = {}
        hostname_return_code, hostname = self._setup_hostname(client)
        if hostname_return_code != 0:
            log.error(
                'Error setting hostname: {0}'.format(hostname_return_code)
            )

        xen_macs = utils.list_xenstore_macaddrs(client)
        for iface in utils.list_hw_interfaces():
            mac = utils.get_hw_addr(iface)

            if not mac or mac not in xen_macs:
                continue

            ifaces[iface] = utils.get_interface(mac, client)

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
            utils.backup_file(interface_config)

        # setup interface files
        for ifname, iface in ifaces.items():
            self._setup_interface(ifname, iface)
            if 'routes' in iface:
                self._setup_routes(ifname, iface)

            """
                Creating servers from custom images may leave IP information
                from the image source. Flush the interface before restart of
                the network to clear out source image IP information
            """
            p = Popen(
                ['ip', 'addr', 'flush', 'dev', ifname],
                stdout=PIPE,
                stderr=PIPE,
                stdin=PIPE
            )
            out, err = p.communicate()
            if p.returncode != 0:
                # Log error and continue to restart network
                log.error('Error flushing interface: {0}'.format(ifname))
        if self.use_network_manager:
            p = Popen(
                ['systemctl', 'restart', 'NetworkManager.service'],
                stdout=PIPE,
                stderr=PIPE,
                stdin=PIPE
            )
        else:
            if os.path.exists('/usr/bin/systemctl'):
                p = Popen(
                    ['systemctl', 'restart', 'network.service'],
                    stdout=PIPE,
                    stderr=PIPE,
                    stdin=PIPE
                )
            else:
                p = Popen(
                    ['service', 'network', 'restart'],
                    stdout=PIPE,
                    stderr=PIPE,
                    stdin=PIPE
                )

        out, err = p.communicate()
        if p.returncode != 0:
            log.error('Error received on network restart: {0}'.format(err))
            return (str(p.returncode), 'Error restarting network')

        return ('0', '')
