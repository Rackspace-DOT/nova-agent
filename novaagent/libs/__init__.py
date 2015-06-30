from __future__ import absolute_import
from novaagent.common.password import PasswordCommands


class DefaultOS(object):
    def keyinit(self, name, value):
        if not hasattr(self, 'p'):
            self.p = PasswordCommands()
        ret = self.p.keyinit_cmd(value)
        return ret

    def password(self, name, value):
        if not hasattr(self, 'p'):
            self.p = PasswordCommands()
        ret = self.p.password_cmd(value)
        return ret

    def injectfile(self, name, value):
        if not hasattr(self, 'f'):
            self.f = FileInject()
        ret = self.f.fileinject_cmd(value)
        return ret


if __name__ == '__main__':
    main()
