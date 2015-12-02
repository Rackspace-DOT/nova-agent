from __future__ import print_function, absolute_import
import argparse
import time
import json
import os
import sys
import argparse
from subprocess import Popen, PIPE

from novaagent import utils
from novaagent.libs import (
    archlinux,
    centos,
    debian,
    freebsd,
    gentoo,
    gentoo_systemd_networkd,
    redhat,
    suse,
)

import logging
log = logging.getLogger(__name__)


def action(serveros):
    for uuid in utils.list_xen_events():
        event = utils.get_xen_event(uuid)
        log.info('Event: {0} -> {1}'.format(uuid, event['name']))
        returncode = ()
        if hasattr(serveros, event['name']):
            cmd = getattr(serveros, event['name'])
            returncode = cmd(event['name'], event['value'])

        utils.remove_xenhost_event(uuid)
        if returncode:
            utils.update_xenguest_event(uuid, {'message': returncode[1], 'returncode': returncode[0]})
            log.info('Returning {{"message": "{1}", "returncode": "{0}"}}'.format(*returncode))
        else:
            utils.update_xenguest_event(uuid, {'message': '', 'returncode': '0'})
            log.info('Returning {"message": "", "returncode": ""}')
        action(serveros)


def main():
    parser = argparse.ArgumentParser(description='Args for novaagent')
    parser.add_argument('-p', dest='pid', type=str, help='pid file')
    parser.add_argument('-l', dest='loglevel', type=str, default='info', choices=('warning', 'info', 'debug'), help='log level')
    parser.add_argument('-o', dest='logfile', default='-', type=str, help='path to log file')
    args = parser.parse_args()

    loglevel = getattr(logging, args.loglevel.upper())
    
    if args.logfile == '-':
        logging.basicConfig(stream=sys.stdout, level=loglevel)
    else:
        logging.basicConfig(filename=args.logfile, level=loglevel)

    if os.path.exists('/etc/arch-release'):
        servertype = archlinux
    elif os.path.exists('/etc/centos-release') \
            or os.path.exists('/etc/fedora-release') \
            or os.path.exists('/etc/sl-release'):
        servertype = centos
    elif os.path.exists('/etc/redhat-release'):
        servertype = redhat
    elif os.path.exists('/etc/debian_version'):
        servertype = debian
    elif os.path.exists('/etc/gentoo-release'):
        servertype = gentoo
        p = Popen(["/bin/pidof", "systemd-networkd"], stdout=PIPE, stderr=PIPE, stdin=PIPE)
        out, err = p.communicate()
        if p.returncode == 0:
            servertype = gentoo_systemd_networkd
    elif os.path.exists('/etc/susehelp.d/'):
        servertype = suse
    elif os.path.exists('/etc/rc.conf'):
        servertype = freebsd

    log.info('Starting actions for {0}...'.format(servertype.__name__))
    serveros = servertype.ServerOS()
    while True:
        if args.pid:
            with open(args.pid, 'w') as pidfile:
                print(os.getpid(), file=pidfile)
        action(serveros)
        time.sleep(1)


if __name__ == '__main__':
    main()
