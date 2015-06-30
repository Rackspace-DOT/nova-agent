from __future__ import print_function, absolute_import
import time
from novaagent import utils


def _main():
    xen_macs = utils.list_xenstore_macaddrs()
    for iface in utils.list_hw_interfaces():
        mac = utils.get_hw_addr(iface)
        if not mac and mac not in xen_macs:
            continue
        print(utils.get_interface(mac))


def main():
    while True:
        time.sleep(1)
        for uuid in utils.list_xen_events():
            event = utils.get_xen_event(uuid)
            utils.remove_xenhost_event(uuid)
            utils.update_xenguest_event(uuid, {'message': json.dumps(event), 'returncode': '0'}):

if __name__ == '__main__':
    main()
