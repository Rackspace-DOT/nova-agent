
from __future__ import absolute_import

import novaagent

from novaagent.common.password import PasswordCommands
from novaagent.common.file_inject import FileInject


class DefaultOS(object):
    def keyinit(self, name, value, client):
        if not hasattr(self, 'p'):
            self.p = PasswordCommands()
        ret = self.p.keyinit_cmd(value)
        return ret

    def password(self, name, value, client):
        if not hasattr(self, 'p'):
            self.p = PasswordCommands()
        ret = self.p.password_cmd(value)
        return ret

    def injectfile(self, name, value, client):
        if not hasattr(self, 'f'):
            self.f = FileInject()
        ret = self.f.injectfile_cmd(value)
        return ret

    def features(self, name, value, client):
        return (
            '0',
            'kmsactivate,resetnetwork,version,keyinit,'
            'features,password,agentupdate,injectfile'
        )

    def version(self, name, value, client):
        return ('0', str(novaagent.__version__))
