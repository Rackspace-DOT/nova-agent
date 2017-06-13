
from __future__ import print_function, absolute_import

import argparse
import time
import os
import sys

from novaagent import utils
from novaagent.libs import (
    centos,
    debian,
    redhat
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
            utils.update_xenguest_event(
                uuid, {
                    'message': returncode[1],
                    'returncode': returncode[0]
                }
            )
            log.info(
                'Returning {{"message": "{1}", "returncode": "{0}"}}'.format(
                    *returncode
                )
            )
        else:
            utils.update_xenguest_event(
                uuid,
                {
                    'message': '',
                    'returncode': '0'
                }
            )
            log.info('Returning {"message": "", "returncode": ""}')
        action(serveros)


def nova_agent_listen(servertype, serveros):
    log.info('Starting actions for {0}...'.format(servertype.__name__))
    while True:
        action(serveros)
        time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description='Args for novaagent')
    parser.add_argument(
        '-l',
        dest='loglevel',
        type=str,
        default='info',
        choices=('warning', 'info', 'debug'),
        help='log level'
    )
    parser.add_argument(
        '-o',
        dest='logfile',
        default='-',
        type=str,
        help='path to log file'
    )
    args = parser.parse_args()

    loglevel = getattr(logging, args.loglevel.upper())

    if args.logfile == '-':
        logging.basicConfig(stream=sys.stdout, level=loglevel)
    else:
        logging.basicConfig(filename=args.logfile, level=loglevel)

    if os.path.exists('/etc/centos-release') \
            or os.path.exists('/etc/fedora-release') \
            or os.path.exists('/etc/sl-release'):
        servertype = centos
    elif os.path.exists('/etc/redhat-release'):
        servertype = redhat
    elif os.path.exists('/etc/debian_version'):
        servertype = debian

    log.info('Starting daemon')
    serveros = servertype.ServerOS()

    try:
        pid = os.fork()
        if pid > 0:
             log.info('PID: {0}'.format(pid))
             os._exit(0)

    except OSError as error:
        log.error(
            'Unable to fork. Error: {0} {1}'.format(
                error.errno,
                error.strerror
            )
        )
        os._exit(1)

    nova_agent_listen(servertype, serveros)


if __name__ == '__main__':
    main()
