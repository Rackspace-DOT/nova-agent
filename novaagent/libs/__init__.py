
from __future__ import absolute_import


import logging
import os


from subprocess import PIPE
from subprocess import Popen


import novaagent


from novaagent.common.password import PasswordCommands
from novaagent.common.file_inject import FileInject
from novaagent import utils


log = logging.getLogger(__name__)


class DefaultOS(object):
    def __init__(self):
        self.hostname_file = '/etc/hostname'

    def keyinit(self, name, value, client):
        if not hasattr(self, 'p'):
            self.p = PasswordCommands()

        return self.p.keyinit_cmd(value)

    def password(self, name, value, client):
        if not hasattr(self, 'p'):
            self.p = PasswordCommands()

        return self.p.password_cmd(value)

    def injectfile(self, name, value, client):
        if not hasattr(self, 'f'):
            self.f = FileInject()

        return self.f.injectfile_cmd(value)

    def features(self, name, value, client):
        return (
            '0',
            'kmsactivate,resetnetwork,version,keyinit,'
            'features,password,injectfile'
        )

    def version(self, name, value, client):
        return ('0', str(novaagent.__version__))

    """
    Common function for all operating systems when setting up hostname
    """
    def _setup_hostname(self, client):
        hostname = utils.get_hostname(client)
        completed = False
        if os.path.exists('/usr/bin/hostnamectl'):
            utils.backup_file(self.hostname_file)
            p = Popen(
                ['hostnamectl', 'set-hostname', hostname],
                stdout=PIPE,
                stderr=PIPE,
                stdin=PIPE
            )
            out, err = p.communicate()
            if p.returncode != 0:
                log.error('Error using hostnamectl: {0}'.format(err))
            else:
                # Do not run hostname since hostnamectl was successful
                completed = True

        if not completed:
            log.debug('Falling back to use hostname command')
            p = Popen(
                ['hostname', hostname],
                stdout=PIPE,
                stderr=PIPE,
                stdin=PIPE
            )
            out, err = p.communicate()
            if p.returncode != 0:
                log.error('Error using hostname: {0}'.format(err))
            else:
                log.debug('Writing file {0}'.format(self.hostname_file))
                with open(self.hostname_file, 'w') as host_file:
                    host_file.write(hostname)

        return p.returncode, hostname
