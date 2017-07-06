
UP2DATE_RETURN = """
# Automatically generated Red Hat Update Agent config file, do not edit.
# Format: 1.0
versionOverride[comment]=Override the automatically determined system version
versionOverride=

enableProxyAuth[comment]=To use an authenticated proxy or not
enableProxyAuth=0

networkRetries[comment]=Number of attempts to make at network connections '''         '''before giving up
networkRetries=5

hostedWhitelist[comment]=None
hostedWhitelist=

enableProxy[comment]=Use a HTTP Proxy
enableProxy=0

serverURL[comment]=Remote server URL
serverURL=https://iadproxy.rhn.rackspace.com/XMLRPC;

proxyPassword[comment]=The password to use for an authenticated proxy
proxyPassword=

noSSLServerURL[comment]=None
noSSLServerURL=http://iadproxy.rhn.rackspace.com/XMLRPC;

proxyUser[comment]=The username for an authenticated proxy
proxyUser=

disallowConfChanges[comment]=Config options that can not be overwritten '''         '''by a config update action
disallowConfChanges=noReboot;sslCACert;useNoSSLForPackages;noSSLServerURL;'''         '''serverURL;disallowConfChanges;

sslCACert[comment]=The CA cert used to verify the ssl server
sslCACert=/usr/share/rhn/RHN-ORG-TRUSTED-SSL-CERT

debug[comment]=Whether or not debugging is enabled
debug=0

httpProxy[comment]=HTTP proxy in host:port format, e.g. squid.redhat.com:3128
httpProxy=

systemIdPath[comment]=Location of system id
systemIdPath=/etc/sysconfig/rhn/systemid

noReboot[comment]=Disable the reboot action
noReboot=0
"""  # noqa


UP2DATE_READLINES = [
    '\n',
    (
        '# Automatically generated Red Hat Update '
        'Agent config file, do not edit.\n'
    ),
    '# Format: 1.0\n',
    (
        'versionOverride[comment]=Override the '
        'automatically determined system version\n'
    ),
    'versionOverride=\n',
    '\n',
    'enableProxyAuth[comment]=To use an authenticated proxy or not\n',
    'enableProxyAuth=0\n',
    '\n',
    (
        "networkRetries[comment]="
        "Number of attempts to make at network connections '''         '''"
        "before giving up\n"
    ),
    'networkRetries=5\n',
    '\n',
    'hostedWhitelist[comment]=None\n',
    'hostedWhitelist=\n',
    '\n',
    'enableProxy[comment]=Use a HTTP Proxy\n',
    'enableProxy=0\n',
    '\n',
    'serverURL[comment]=Remote server URL\n',
    'serverURL=https://iadproxy.rhn.rackspace.com/XMLRPC;\n',
    '\n',
    'proxyPassword[comment]=The password to use for an authenticated proxy\n',
    'proxyPassword=\n',
    '\n',
    'noSSLServerURL[comment]=None\n',
    'noSSLServerURL=http://iadproxy.rhn.rackspace.com/XMLRPC;\n',
    '\n',
    'proxyUser[comment]=The username for an authenticated proxy\n',
    'proxyUser=\n',
    '\n',
    (
        "disallowConfChanges[comment]="
        "Config options that can not be overwritten '''         '''"
        "by a config update action\n"
    ),
    (
        "disallowConfChanges=noReboot;sslCACert;useNoSSLForPackages;"
        "noSSLServerURL;'''         '''serverURL;disallowConfChanges;\n"
    ),
    '\n',
    'sslCACert[comment]=The CA cert used to verify the ssl server\n',
    'sslCACert=/usr/share/rhn/RHN-ORG-TRUSTED-SSL-CERT\n',
    '\n',
    'debug[comment]=Whether or not debugging is enabled\n',
    'debug=0\n',
    '\n',
    (
        'httpProxy[comment]=HTTP proxy in host:port '
        'format, e.g. squid.redhat.com:3128\n'
    ),
    'httpProxy=\n',
    '\n',
    'systemIdPath[comment]=Location of system id\n',
    'systemIdPath=/etc/sysconfig/rhn/systemid\n',
    '\n',
    'noReboot[comment]=Disable the reboot action\n',
    'noReboot=0\n',
    '\n'
]
