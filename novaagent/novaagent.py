from __future__ import print_function, absolute_import
import time
import json
from novaagent import utils


def _main():
    xen_macs = utils.list_xenstore_macaddrs()
    for iface in utils.list_hw_interfaces():
        mac = utils.get_hw_addr(iface)
        if not mac and mac not in xen_macs:
            continue
        print(utils.get_interface(mac))


def action():
    for uuid in utils.list_xen_events():
        event = utils.get_xen_event(uuid)
        print(event)
        print(uuid)
        if event['name'] == 'version':
            utils.remove_xenhost_event(uuid)
            utils.update_xenguest_event(uuid, {'message': '1.39.1', 'returncode': '0'})
        else:
            utils.remove_xenhost_event(uuid)
            utils.update_xenguest_event(uuid, {'message': '', 'returncode': '0'})
        action()


def main():
    while True:
        action()
        time.sleep(1)


if __name__ == '__main__':
    main()
