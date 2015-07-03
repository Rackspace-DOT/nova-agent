# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
#  Copyright (c) 2011 Openstack, LLC.
#  All Rights Reserved.
#
#     Licensed under the Apache License, Version 2.0 (the "License"); you may
#     not use this file except in compliance with the License. You may obtain
#     a copy of the License at
#
#          http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#     WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#     License for the specific language governing permissions and limitations
#     under the License.
#

"""
redhat/centos KMS activation helper module
"""

import os
import subprocess
import logging

import commands.network

RHN_PATH = '/etc/sysconfig/rhn'
SYSTEMID_PATH = os.path.join(RHN_PATH, 'systemid')
UP2DATE_PATH = os.path.join(RHN_PATH, 'up2date')


def register_with_rhn(activation_key, profile):
    if os.path.exists(SYSTEMID_PATH):
        os.unlink(SYSTEMID_PATH)

    # Call rhnreg_ks
    logging.debug('executing /usr/sbin/rhnreg_ks --activationkey <REMOVED>' + \
            ' --profile %s --force' % profile)
    pipe = subprocess.PIPE
    p = subprocess.Popen(['/usr/sbin/rhnreg_ks', '--activationkey',
            activation_key, '--profile', profile, '--force'],
            stdin=pipe, stdout=pipe, stderr=pipe, env={})
    logging.debug('waiting on pid %d' % p.pid)
    status = os.waitpid(p.pid, 0)[1]
    logging.debug('status = %d' % status)

    if status != 0:
        return (500, "Couldn't activate with RHN: %d" % status)


def configure_up2date(domains):
    if not isinstance(domains, list):
        domains = [domains]

    domains = ['//%s/XMLRPC' % d for d in domains]

    serverURL = ';'.join(['https:%s' % h for h in domains])
    noSSLServerURL = ';'.join(['http:%s' % h for h in domains])

    data = \
'''# Automatically generated Red Hat Update Agent config file, do not edit.
# Format: 1.0
versionOverride[comment]=Override the automatically determined system version
versionOverride=

enableProxyAuth[comment]=To use an authenticated proxy or not
enableProxyAuth=0

networkRetries[comment]=Number of attempts to make at network connections ''' \
        '''before giving up
networkRetries=5

hostedWhitelist[comment]=None
hostedWhitelist=

enableProxy[comment]=Use a HTTP Proxy
enableProxy=0

serverURL[comment]=Remote server URL
serverURL=%(serverURL)s;

proxyPassword[comment]=The password to use for an authenticated proxy
proxyPassword=

noSSLServerURL[comment]=None
noSSLServerURL=%(noSSLServerURL)s;

proxyUser[comment]=The username for an authenticated proxy
proxyUser=

disallowConfChanges[comment]=Config options that can not be overwritten ''' \
        '''by a config update action
disallowConfChanges=noReboot;sslCACert;useNoSSLForPackages;noSSLServerURL;''' \
        '''serverURL;disallowConfChanges;

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
''' % {'serverURL': serverURL,
       'noSSLServerURL': noSSLServerURL}

    return {UP2DATE_PATH: data}


def kms_activate(data):
    activation_key = data['activation_key']
    profile = data['profile']

    domains = data['domains']

    update_files = configure_up2date(domains)
    commands.network.update_files(update_files)

    ret = register_with_rhn(activation_key, profile)
    if ret:
        return ret

    return (0, "")
