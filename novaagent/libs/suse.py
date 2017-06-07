from __future__ import print_function, absolute_import
import os
import re
from tempfile import mkstemp
from shutil import move

from novaagent import utils
from subprocess import Popen, PIPE

from novaagent.libs import DefaultOS


class ServerOS(DefaultOS):
    def _setup_interface(self, ifname, iface):
        utils.backup_file('/etc/sysconfig/network/ifcfg-{0}'.format(ifname))
        with open(
            '/etc/sysconfig/network/ifcfg-{0}'.format(ifname),
            'w'
        ) as iffile:
            print('# Label {0}'.format(iface['label']), file=iffile)
            print('BOOTPROTO=static', file=iffile)
            ifnum = None
            for x in iface['ips']:
                if ifnum is None:
                    print('IPADDR={0}'.format(x['ip']), file=iffile)
                    print('NETMASK={0}'.format(x['netmask']), file=iffile)
                    ifnum = 0
                else:
                    print('IPADDR_{0}={1}'.format(ifnum, x['ip']), file=iffile)
                    print(
                        'NETMASK_{0}={1}'.format(ifnum, x['netmask']),
                        file=iffile
                    )
                    print('LABEL_{0}={0}'.format(ifnum), file=iffile)
                    ifnum += 1

            if 'ip6s' in iface and iface['ip6s']:
                for x in iface['ip6s']:
                    if ifnum is None:
                        print('IPADDR={0}'.format(x['ip']), file=iffile)
                        print(
                            'PREFIXLEN_{0}={1}'.format(ifnum, x['netmask']),
                            file=iffile
                        )
                        ifnum = 0
                    else:
                        print(
                            'IPADDR_{0}={1}'.format(ifnum, x['ip']),
                            file=iffile
                        )
                        print(
                            'PREFIXLEN_{0}={1}'.format(ifnum, x['netmask']),
                            file=iffile
                        )
                        print('LABEL_{0}={0}'.format(ifnum), file=iffile)
                        ifnum += 1

            print("STARTMODE='auto'", file=iffile)
            print("USERCONTROL='no'", file=iffile)

    def _setup_routes(self, ifname, iface):
        utils.backup_file('/etc/sysconfig/network/ifroute-{0}'.format(ifname))
        with open(
            '/etc/sysconfig/network/ifroute-{0}'.format(ifname),
            'w'
        ) as routefile:
            print('# Label {0}'.format(iface['label']), file=routefile)
            if 'gateway' in iface and iface['gateway']:
                print(
                    'default {0} - -'.format(iface['gateway']),
                    file=routefile
                )

            if 'gateway_v6' in iface and iface['gateway_v6']:
                print(
                    'default {0} - -'.format(iface['gateway_v6']),
                    file=routefile
                )

            if 'routes' in iface and iface['routes']:
                for route in iface['routes']:
                    print(
                        '{route} {gateway} {netmask} {0}'.format(
                            ifname,
                            **route
                        ),
                        file=routefile
                    )

    def _setup_dns(self, ifname, iface):
        if 'dns' not in iface:
            return
        newline = 'NETCONFIG_DNS_STATIC_SERVERS="{0}"\n'.format(
            ' '.join(iface['dns'])
        )
        config = '/etc/sysconfig/network/config'
        fh, abs_path = mkstemp()
        nochange = False
        with open(abs_path, 'w') as newfile:
            with open(config) as conffile:
                for line in conffile:
                    if re.search('^NETCONFIG_DNS_STATIC_SERVERS=', line):
                        if line == newline:
                            nochange = True
                            break
                        line = newline
                    newfile.write(line)
        os.close(fh)
        if nochange:
            os.remove(abs_path)
        else:
            utils.backup_file(config)
            os.remove(config)
            move(abs_path, config)

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
        utils.backup_file('/etc/HOSTNAME')
        with open('/etc/HOSTNAME', 'w') as hostfile:
            print(hostname, file=hostfile)
        if os.path.exists('/usr/bin/hostnamectl'):
            utils.backup_file('/etc/hostname')
            p = Popen(
                ['hostnamectl', 'set-hostname', hostname],
                stdout=PIPE,
                stderr=PIPE,
                stdin=PIPE
            )
            out, err = p.communicate()
            if p.returncode != 0:
                return (str(p.returncode), 'Error setting hostname')
        else:
            p = Popen(
                ['hostname', hostname],
                stdout=PIPE,
                stderr=PIPE,
                stdin=PIPE
            )
            out, err = p.communicate()
            if p.returncode != 0:
                return (str(p.returncode), 'Error setting hostname')

        # setup interface files
        for ifname, iface in ifaces.items():
            self._setup_interface(ifname, iface)
            self._setup_routes(ifname, iface)
            self._setup_dns(ifname, iface)

        p = Popen(
            ['systemctl', 'restart', 'network.service'],
            stdout=PIPE,
            stderr=PIPE,
            stdin=PIPE
        )
        out, err = p.communicate()
        if p.returncode != 0:
            return (str(p.returncode), 'Error restarting network')

        return ('0', '')
