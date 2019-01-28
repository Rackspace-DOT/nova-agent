
CENTOS_ROUTE_FILE = [
    'ADDRESS0=10.208.0.0\n',
    'NETMASK0=255.240.0.0\n',
    'GATEWAY0=10.208.224.1\n',
    'ADDRESS1=10.176.0.0\n',
    'NETMASK1=255.240.0.0\n',
    'GATEWAY1=10.208.224.1\n'
]

CENTOS_IFCFG_ETH1 = [
    '# Automatically generated, do not edit\n',
    '\n',
    '# Label private\n',
    'BOOTPROTO=static\n',
    'DEVICE=eth1\n',
    'IPADDR=10.208.227.239\n',
    'NETMASK=255.255.224.0\n',
    'ONBOOT=yes\n',
    'NM_CONTROLLED=no\n',
    'ZONE=TestFirewalldZone\n',
    'TEST_OPTION=TEST_VALUE\n'
]

CENTOS_IFCFG_ETH0 = [
    '# Automatically generated, do not edit\n',
    '\n',
    '# Label public\n',
    'BOOTPROTO=static\n',
    'DEVICE=eth0\n',
    'IPADDR=104.130.4.72\n',
    'NETMASK=255.255.255.0\n',
    'IPADDR1=104.130.4.73\n',
    'NETMASK1=255.255.255.0\n',
    'GATEWAY=104.130.4.1\n',
    'IPV6INIT=yes\n',
    'IPV6ADDR=2001:4802:7802:104:be76:4eff:fe20:7572/64\n',
    'IPV6ADDR1=2001:4802:7802:104:be76:4eff:fe20:7573/64\n',
    'IPV6_DEFAULTGW=fe80::def%eth0\n',
    'DNS1=69.20.0.164\n',
    'DNS2=69.20.0.196\n',
    'ONBOOT=yes\n',
    'NM_CONTROLLED=no\n',
    'ZONE=TestFirewalldZone\n',
    'TEST_OPTION=TEST_VALUE\n'
]

ETH0_INTERFACE = {
    'ip6s': [
        {
            'ip': '2001:4802:7802:104:be76:4eff:fe20:7572',
            'netmask': 64,
            'enabled': '1',
            'gateway': 'fe80::def'
        }, {
            'ip': '2001:4802:7802:104:be76:4eff:fe20:7573',
            'netmask': 64,
            'enabled': '1',
            'gateway': 'fe80::def'
        }
    ],
    'label': 'public',
    'broadcast': '104.130.4.255',
    'ips': [
        {
            'ip': '104.130.4.72',
            'netmask': '255.255.255.0',
            'enabled': '1',
            'gateway': '104.130.4.1'
        }, {
            'ip': '104.130.4.73',
            'netmask': '255.255.255.0',
            'enabled': '1',
            'gateway': '104.130.4.1'
        }
    ],
    'mac': 'BC:76:4E:20:75:72',
    'gateway_v6': 'fe80::def',
    'dns': [
        '69.20.0.164',
        '69.20.0.196'
    ],
    'gateway': '104.130.4.1'
}

ALL_INTERFACES = {
    'eth2': {
        'broadcast': '192.168.5.255',
        'ips': [
            {
                'ip': '192.168.5.4',
                'netmask': '255.255.255.0',
                'enabled': '1',
                'gateway': None
            }
        ],
        'mac': 'BC:76:4E:20:3B:70',
        'gateway': None,
        'label': 'test-interface-2'
    },
    'eth0': {
        'ip6s': [
            {
                'ip': '2001:4802:7803:104:be76:4eff:fe20:5eb2',
                'netmask': 64,
                'enabled': '1',
                'gateway': 'fe80::def'
            }
        ],
        'label': 'public',
        'broadcast': '104.130.169.255',
        'ips': [
            {
                'ip': '104.130.169.159',
                'netmask': '255.255.255.0',
                'enabled': '1',
                'gateway': '104.130.169.1'
            }
        ],
        'mac': 'BC:76:4E:20:5E:B2',
        'gateway_v6': 'fe80::def',
        'dns': ['69.20.0.164', '69.20.0.196'],
        'gateway': '104.130.169.1'
    },
    'eth1': {
        'label': 'private',
        'broadcast': '10.176.223.255',
        'ips': [
            {
                'ip': '10.176.195.183',
                'netmask': '255.255.224.0',
                'enabled': '1',
                'gateway': None
            }
        ],
        'mac': 'BC:76:4E:20:5E:FB',
        'routes': [
            {
                'route': '10.208.0.0',
                'netmask': '255.240.0.0',
                'gateway': '10.176.192.1'
            }, {
                'route': '10.176.0.0',
                'netmask': '255.240.0.0',
                'gateway': '10.176.192.1'
            }
        ],
        'gateway': None
    }
}

ALPINE_INTERFACES_CONFIG = [
    '#This is a test file\n',
    '# Label public\n',
    '\n',
    'auto eth0\n',
    'iface eth0 inet static\n',
    '\taddress 104.130.4.72\n',
    '\tnetmask 255.255.255.0\n',
    '\tgateway 104.130.4.1\n',
    '\tdns-nameservers 69.20.0.164 69.20.0.196\n',
    '\n',
    'auto eth0:1\n',
    'iface eth0:1 inet static\n',
    '\taddress 104.130.4.73\n',
    '\tnetmask 255.255.255.0\n',
    '\n',
    'iface eth0 inet6 static\n',
    '\taddress 2001:4802:7802:104:be76:4eff:fe20:7572\n',
    '\tnetmask 64\n',
    '\tgateway fe80::def\n',
    '\n',
    'iface eth0:1 inet6 static\n',
    '\taddress 2001:4802:7802:104:be76:4eff:fe20:7573\tnetmask 64\n',
    '\n',
    '# Label private\n',
    '\n',
    'auto eth1\n',
    'iface eth1 inet static\n',
    '\taddress 10.208.227.239\n',
    '\tnetmask 255.255.224.0\n',
    (
        '\tpost-up route add -net 10.208.0.0 netmask 255.'
        '240.0.0 gw 10.208.224.1 || true\n'
    ),
    (
        '\tpost-down route add -net 10.208.0.0 netmask 255.'
        '240.0.0 gw 10.208.224.1 || true\n'
    ),
    (
        '\tpost-up route add -net 10.176.0.0 netmask 255.'
        '240.0.0 gw 10.208.224.1 || true\n'
    ),
    (
        '\tpost-down route add -net 10.176.0.0 netmask 255.'
        '240.0.0 gw 10.208.224.1 || true\n'
    ),
    '\n'
]

ALPINE_INTERFACES_LOOPBACK = [
    '# The loopback network interface\n',
    'auto lo\n',
    'iface lo inet loopback\n',
    '\n'
]

CENTOS_NETWORK_FILE = [
    'NETWORKING=yes\n',
    'NOZEROCONF=yes\n',
    'NETWORKING_IPV6=yes\n',
    'HOSTNAME=test_hostname\n'
]

DEBIAN_INTERFACES_CONFIG = [
    '#This is a test file\n',
    '# Label public\n',
    '\n',
    'auto eth0\n',
    'iface eth0 inet static\n',
    '\taddress 104.130.4.72\n',
    '\tnetmask 255.255.255.0\n',
    '\tgateway 104.130.4.1\n',
    '\tdns-nameservers 69.20.0.164 69.20.0.196\n',
    '\n',
    'auto eth0:1\n',
    'iface eth0:1 inet static\n',
    '\taddress 104.130.4.73\n',
    '\tnetmask 255.255.255.0\n',
    '\n',
    'iface eth0 inet6 static\n',
    '\taddress 2001:4802:7802:104:be76:4eff:fe20:7572\n',
    '\tnetmask 64\n',
    '\tgateway fe80::def\n',
    '\n',
    'iface eth0:1 inet6 static\n',
    '\taddress 2001:4802:7802:104:be76:4eff:fe20:7573\tnetmask 64\n',
    '\n',
    '# Label private\n',
    '\n',
    'auto eth1\n',
    'iface eth1 inet static\n',
    '\taddress 10.208.227.239\n',
    '\tnetmask 255.255.224.0\n',
    (
        '\tpost-up route add -net 10.208.0.0 netmask 255.'
        '240.0.0 gw 10.208.224.1 || true\n'
    ),
    (
        '\tpost-down route add -net 10.208.0.0 netmask 255.'
        '240.0.0 gw 10.208.224.1 || true\n'
    ),
    (
        '\tpost-up route add -net 10.176.0.0 netmask 255.'
        '240.0.0 gw 10.208.224.1 || true\n'
    ),
    (
        '\tpost-down route add -net 10.176.0.0 netmask 255.'
        '240.0.0 gw 10.208.224.1 || true\n'
    ),
    '\n'
]

DEBIAN_NETPLAN_CONFIG = [
    'network:\n',
    '  ethernets:\n',
    '    eth0:\n',
    '      addresses:\n',
    '      - 104.130.4.72/24\n',
    '      - 104.130.4.73/24\n',
    '      - 2001:4802:7802:104:be76:4eff:fe20:7572/64\n',
    '      - 2001:4802:7802:104:be76:4eff:fe20:7573/64\n',
    '      dhcp4: false\n',
    '      dhcp6: false\n',
    '      gateway4: 104.130.4.1\n',
    '      gateway6: fe80::def\n',
    '      nameservers:\n',
    '        addresses:\n',
    '        - 69.20.0.164\n',
    '        - 69.20.0.196\n',
    '    eth1:\n',
    '      addresses:\n',
    '      - 10.208.227.239/19\n',
    '      dhcp4: false\n',
    '      routes:\n',
    '      - to: 10.208.0.0/12\n',
    '        via: 10.208.224.1\n',
    '      - to: 10.176.0.0/12\n',
    '        via: 10.208.224.1\n',
    '  renderer: networkd\n',
    '  version: 2\n'
]

DEBIAN_INTERFACES_LOOPBACK = [
    '# The loopback network interface\n',
    'auto lo\n',
    'iface lo inet loopback\n',
    '\n'
]

UBUNTU_NETPLAN_CONFIG = [
    'network:\n',
    '  ethernets:\n',
    '    eth0:\n',
    '      addresses:\n',
    '      - 104.130.169.159/24\n',
    '      - 2001:4802:7803:104:be76:4eff:fe20:5eb2/64\n',
    '      dhcp4: false\n',
    '      dhcp6: false\n',
    '      gateway4: 104.130.169.1\n',
    '      gateway6: fe80::def\n',
    '      nameservers:\n',
    '        addresses:\n',
    '        - 69.20.0.164\n',
    '        - 69.20.0.196\n',
    '    eth1:\n',
    '      addresses:\n',
    '      - 10.176.195.183/19\n',
    '      dhcp4: false\n',
    '      routes:\n',
    '      - to: 10.208.0.0/12\n',
    '        via: 10.176.192.1\n',
    '      - to: 10.176.0.0/12\n',
    '        via: 10.176.192.1\n',
    '    eth2:\n',
    '      addresses:\n',
    '      - 192.168.5.4/24\n',
    '      dhcp4: false\n',
    '  renderer: networkd\n',
    '  version: 2\n'
]
