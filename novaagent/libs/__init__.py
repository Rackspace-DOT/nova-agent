from __future__ import absolute_import
from novaagent.common.password import PasswordCommands


class DefaultOS(object):
    def keyinit(self, name, value):
        p = PasswordCommands()
        ret = p.keyinit_cmd(value)
        return ret

    def password(self, name, value):
        p = PasswordCommands()
        ret = p.password_cmd(value)
        return ret


if __name__ == '__main__':
    main()
