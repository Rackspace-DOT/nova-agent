
def get_hostname(use_bytes=True):
    if use_bytes:
        return b'test-server\n'
    else:
        return 'test-server'


def get_xen_host_events():
    return [
        b'748dee41-c47f-4ec7-b2cd-037e51da4031'
    ]


def get_xen_host_event_details():
    return (
        b'{"name": "keyinit", "value": "68436575764933852815830951574296"}\n'
    )


def get_mac_addresses():
    return [
        b'BC764E206C5B',
        b'BC764E206C5A'
    ]


def get_network_interface():
    return b"""
{"label": "private", "broadcast": "10.208.255.255", "ips": [
{"ip": "10.208.227.239", "netmask": "255.255.224.0", "enabled": "1",
"gateway": null}], "mac": "BC:76:4E:20:6C:5B", "routes": [
{"route": "10.208.0.0", "netmask": "255.240.0.0", "gateway": "10.208.224.1"},
{"route": "10.176.0.0", "netmask": "255.240.0.0", "gateway": "10.208.224.1"}],
"gateway": null}\n"""


def check_network_interface():
    return {
        'label': 'private',
        'ips': [
            {
                'ip': '10.208.227.239',
                'gateway': None,
                'enabled': '1',
                'netmask': '255.255.224.0'
            }
        ],
        'broadcast': '10.208.255.255',
        'mac': 'BC:76:4E:20:6C:5B',
        'gateway': None,
        'routes': [
            {
                'gateway': '10.208.224.1',
                'route': '10.208.0.0',
                'netmask': '255.240.0.0'
            }, {
                'gateway': '10.208.224.1',
                'route': '10.176.0.0',
                'netmask': '255.240.0.0'
            }
        ]
    }


def get_iface_from_netifaces():
    return {
        17: [
            {
                'broadcast': 'ff:ff:ff:ff:ff:ff',
                'addr': 'bc:76:4e:20:5a:79'
            }
        ],
        2: [
            {
                'broadcast': '10.176.223.255',
                'netmask': '255.255.224.0',
                'addr': '10.176.198.15'
            }
        ],
        10: [
            {
                'netmask': 'ffff:ffff:ffff:ffff::',
                'addr': 'fe80::be76:4eff:fe20:5a79%eth1'
            }
        ]
    }


FCNTL_INFO = 'eth1\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\xbcvN l[\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'  # noqa
