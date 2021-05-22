
from __future__ import absolute_import


import argparse
import logging
import time
import sys
import os


from pyxs.connection import XenBusConnection
from pyxs.client import Client


from novaagent.xenstore.ProcXenBus import ProcXenBus
from novaagent.xenbus import XenGuestRouter
from novaagent.libs import alpine
from novaagent.libs import centos
from novaagent.libs import debian
from novaagent.libs import redhat
from novaagent import utils
from novaagent import __version__


log = logging.getLogger(__name__)


# Connect to Xenbus in order to interact with xenstore
XENBUS_ROUTER = XenGuestRouter(XenBusConnection())


def action(server_os, client=None):
    # Return whether or not to trigger init notification
    trigger_notify = False

    xen_events = utils.list_xen_events(client)
    if len(xen_events) == 0:
        # if no xen_events then trigger the notification
        trigger_notify = True

    for uuid in xen_events:
        event = utils.get_xen_event(uuid, client)
        if 'name' not in event:
            log.error('Event Not Supported: {0} -> {1}'.format(uuid, event))
            continue
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
        if event['name'] == 'resetnetwork':
            # If the network has completed setup then trigger the notification
            trigger_notify = True

    return trigger_notify


def nova_agent_listen(server_type, server_os, notify, server_init):
    log.info('Starting actions for {0}'.format(server_type.__name__))
    log.info('Checking for existence of /dev/xen/xenbus')

    send_notification = True
    notify_init = False

    if os.path.exists('/dev/xen/xenbus'):
        with Client(router=XENBUS_ROUTER) as xenbus_client:
            check_provider(utils.get_provider(client=xenbus_client))
            while True:
                notify_init = action(server_os, client=xenbus_client)
                if send_notification and notify_init:
                    log.info('Sending notification startup is complete')
                    utils.send_notification(server_init, notify)
                    send_notification = False

                time.sleep(10)

    elif os.path.exists('/proc/xen/xenbus'):
        log.info('Using /proc/xen/xenbus')
        with ProcXenBus() as proc_xenbus_client:
            check_provider(utils.get_provider(client=proc_xenbus_client))
            while True:
                notify_init = action(server_os, client=proc_xenbus_client)
                if send_notification and notify_init:
                    log.info('Sending notification startup is complete')
                    utils.send_notification(server_init, notify)
                    send_notification = False

                time.sleep(10)
    else:
        check_provider(utils.get_provider())
        while True:
            notify_init = action(server_os)
            if send_notification and notify_init:
                log.info('Sending notification startup is complete')
                utils.send_notification(server_init, notify)
                send_notification = False

            time.sleep(10)


def get_server_type():
    server_type = None
    if os.path.exists('/etc/alpine-release'):
        server_type = alpine
    elif (
        os.path.exists('/etc/centos-release') or
        os.path.exists('/etc/fedora-release')
    ):
        server_type = centos
    elif os.path.exists('/etc/redhat-release'):
        server_type = redhat
    elif os.path.exists('/etc/debian_version'):
        server_type = debian

    return server_type


def get_init_system():
    # Checking for systemd on OS
    try:
        os.stat('/run/systemd/system')
        log.debug('Systemd is the init system')
        return 'systemd'
    except Exception:
        pass

    # Check if upstart system was used to start agent
    upstart_job = os.environ.get('UPSTART_JOB', None)

    # RHEL 6 and CentOS 6 use rc upstart job to start all the SysVinit
    # emulation layer instead of individual init scripts
    if upstart_job not in (None, 'rc'):
        log.debug('Upstart job that started script: {0}'.format(upstart_job))
        return 'upstart'

    # return None and no notifications to init system will occur
    log.debug('SysVinit is the init system')
    return None


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
    parser.add_argument(
        '--version',
        default=False,
        action='store_true',
        help='Display version and exit'
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

    if args.version:
        print(__version__)
        return

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

    log.info('Agent is starting up')
    server_type = get_server_type()
    server_os = server_type.ServerOS()
    server_init = get_init_system()
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

    notify = None
    if server_init == 'systemd':
        notify = utils.notify_socket()

    nova_agent_listen(server_type, server_os, notify, server_init)


if __name__ == '__main__':
    main()
