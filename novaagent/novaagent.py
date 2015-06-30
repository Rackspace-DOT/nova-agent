from __future__ import print_function, absolute_import
import argparse
import time
import json
import os
import sys
from novaagent import utils
from novaagent.libs import (
    archlinux,
    freebsd,
)

import argparse


def _main():
    xen_macs = utils.list_xenstore_macaddrs()
    for iface in utils.list_hw_interfaces():
        mac = utils.get_hw_addr(iface)
        if not mac and mac not in xen_macs:
            continue
        print(utils.get_interface(mac))


def action(serveros):
    for uuid in utils.list_xen_events():
        event = utils.get_xen_event(uuid)
        returncode = '0'
        if hasattr(serveros, event['name']):
            cmd = getattr(serveros, event['name'])
            returncode = cmd(event['name'], event['value'])

        utils.remove_xenhost_event(uuid)
        if event['name'] == 'version':
            utils.update_xenguest_event(uuid, {'message': '1.39.1', 'returncode': '0'})
        elif event['name'] == 'keyinit':
            utils.update_xenguest_event(uuid, {'message': returncode[1], 'returncode': returncode[0]})
        else:
            utils.update_xenguest_event(uuid, {'message': '', 'returncode': '0'})
        action(serveros)


def main():
    parser = argparse.ArgumentParser(description='Args for novaagent')
    parser.add_argument('-f', dest='fork', action='store_true', help='fork into background')
    parser.add_argument('-p', dest='pid', type=str, help='pid file')
    args = parser.parse_args()

    if os.path.exists('/etc/arch-release'):
        serveros = archlinux.ServerOS()
    elif os.path.exists('/etc/rc.conf'):
        serveros = freebsd.ServerOS()

    while True:
        if args.fork:
            pid = os.fork()
            if pid:
                if args.pid:
                    with open(args.pid, 'w') as pidfile:
                        print(pid, file=pidfile)
                sys.exit()
        action(serveros)
        time.sleep(1)


if __name__ == '__main__':
    main()
