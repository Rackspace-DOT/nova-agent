
CENTOS_ROUTE_FILE = [
    'ADDRESS0=10.208.0.0\n',
    'NETMASK0=255.240.0.0\n',
    'GATEWAY0=10.208.224.1\n',
    'ADDRESS1=10.176.0.0\n',
    'NETMASK1=255.240.0.0\n',
    'GATEWAY1=10.208.224.1\n'
]

CENTOS_IFCFG_ETH1 = [
    '# Label private\n',
    'BOOTPROTO=static\n',
    'DEVICE=eth1\n',
    'IPADDR=10.208.227.239\n',
    'NETMASK=255.255.224.0\n',
    'ONBOOT=yes\n',
    'NM_CONTROLLED=no\n'
]

CENTOS_IFCFG_ETH0 = [
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
    'NM_CONTROLLED=no\n'
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

CENTOS_NETWORK_FILE = [
    'NETWORKING=yes\n',
    'NOZEROCONF=yes\n',
    'NETWORKING_IPV6=yes\n',
    'HOSTNAME=test_hostname\n'
]
