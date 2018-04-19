
from __future__ import print_function
from __future__ import absolute_import


import argparse
import logging
import time
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


_ready = False


def notify_ready():
    """
    Use systemd notify protocol, or upstart sigstop, to notify
    rediness of the nova-agent.
    """

    global _ready

    if _ready:
        return

    # PyPI edition of python-systemd
    try:
        from systemd.daemon import notify, Notification
        notify(Notification.READY)
    # Older v234 python-systemd
    except ImportError:
        try:
            from systemd.daemon import notify
            notify('READY=1')
        except ImportError:
            pass

    # Upstart notification type
    if os.environ.get('UPSTART_JOB'):
        import signal
        os.kill(os.getpid(), signal.SIGSTOP)

    _ready = True


def nova_agent_listen(server_type, server_os):
    log.info('Starting actions for {0}'.format(server_type.__name__))
    log.info('Checking for existence of /dev/xen/xenbus')
    if os.path.exists('/dev/xen/xenbus'):
        with Client(router=XENBUS_ROUTER) as xenbus_client:
            check_provider(utils.get_provider(client=xenbus_client))
            while True:
                action(server_os, client=xenbus_client)
                notify_ready()
                time.sleep(1)
    else:
        check_provider(utils.get_provider())
        while True:
            action(server_os)
            notify_ready()
            time.sleep(1)


def get_server_type():
    server_type = None
    if (
        os.path.exists('/etc/centos-release') or
        os.path.exists('/etc/fedora-release')
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
        action='store_true',
        help='Perform os.fork when starting agent'
    )
    return parser


def check_provider(provider):
    if provider is None or provider.lower() != 'rackspace':
        log.error('Invalid provider for instance, agent will exit')
        os._exit(1)

    return


def main():
    parser = create_parser()
    args = parser.parse_args()
    loglevel = getattr(logging, args.loglevel.upper())
    log_format = "%(asctime)s [%(levelname)-5.5s] %(message)s"
    if args.logfile == '-':
        logging.basicConfig(
            stream=sys.stdout,
            level=loglevel,
            format=log_format
        )
    else:
        logging.basicConfig(
            filename=args.logfile,
            level=loglevel,
            format=log_format
        )

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


if __name__ == '__main__':
    main()
