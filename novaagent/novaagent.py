
from __future__ import print_function
from __future__ import absolute_import


import argparse
import logging
import fcntl
import time
import stat
import sys
import os


from pyxs.connection import XenBusConnection
from pyxs.client import Client


from novaagent.xenbus import XenGuestRouter
from novaagent.libs import centos
from novaagent.libs import debian
from novaagent.libs import redhat
from novaagent import utils


log = logging.getLogger(__name__)


# Connect to Xenbus in order to interact with xenstore
XENBUS_ROUTER = XenGuestRouter(XenBusConnection())


class AgentRunning(Exception):
    pass


def action(server_os, client=None):
    for uuid in utils.list_xen_events(client):
        event = utils.get_xen_event(uuid, client)
        log.info('Event: {0} -> {1}'.format(uuid, event['name']))
        command_return = ('', '')
        if hasattr(server_os, event['name']):
            run_command = getattr(server_os, event['name'])
            command_return = run_command(event['name'], event['value'], client)

        utils.remove_xenhost_event(uuid, client)
        message = command_return[1]
        return_code = command_return[0]
        if command_return[0] == '':
            return_code = '0'

        utils.update_xenguest_event(
            uuid,
            {'message': message, 'returncode': return_code},
            client
        )
        log.info(
            'Returning {{"message": "{0}", "returncode": "{1}"}}'.format(
                message,
                return_code
            )
        )


def nova_agent_listen(server_type, server_os):
    log.info('Setting lock on file')
    create_lock_file()
    log.info('Starting actions for {0}...'.format(server_type.__name__))
    log.info('Checking for existence of /dev/xen/xenbus')
    if os.path.exists('/dev/xen/xenbus'):
        with Client(router=XENBUS_ROUTER) as xenbus_client:
            while True:
                action(server_os, client=xenbus_client)
                time.sleep(1)
    else:
        while True:
            action(server_os)
            time.sleep(1)


def get_server_type():
    server_type = None
    if (
        os.path.exists('/etc/centos-release') or
        os.path.exists('/etc/fedora-release') or
        os.path.exists('/etc/sl-release')
    ):
        server_type = centos
    elif os.path.exists('/etc/redhat-release'):
        server_type = redhat
    elif os.path.exists('/etc/debian_version'):
        server_type = debian

    return server_type


def create_parser():
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
    parser.add_argument(
        '--no-fork',
        dest='no_fork',
        default=False,
        type=bool,
        help='Perform os.fork when starting agent'
    )
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    loglevel = getattr(logging, args.loglevel.upper())
    if args.logfile == '-':
        logging.basicConfig(stream=sys.stdout, level=loglevel)
    else:
        logging.basicConfig(filename=args.logfile, level=loglevel)

    server_type = get_server_type()
    server_os = server_type.ServerOS()
    if args.no_fork is False:
        log.info('Starting daemon')
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
    else:
        log.info('Skipping os.fork as directed by arguments')

    nova_agent_listen(server_type, server_os)


def create_lock_file():
    """
        Try to create a lock file in order to keep only one instance of the
        agent running.

        Lock file will be at /tmp/.nova-agent.lock.

        Also making sure that all users can write to it as the agent could be
        started by a non root user.
    """
    lf_path = os.path.join('/tmp', '.nova-agent.lock')
    log.info('Creating lock file {0}'.format(lf_path))
    lf_flags = os.O_WRONLY | os.O_CREAT
    lf_mode = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH

    umask_original = os.umask(0)
    try:
        lf_fd = os.open(lf_path, lf_flags, lf_mode)
    finally:
        os.umask(umask_original)

    # Try locking the file
    try:
        fcntl.lockf(lf_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        raise AgentRunning(
            'Agent may already be running and only one instance of it can run '
            'at a time.'
        )

    return


if __name__ == '__main__':
    main()
