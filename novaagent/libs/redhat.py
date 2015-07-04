from __future__ import print_function, absolute_import
import os

from novaagent import utils
from novaagent.common import kms
import novaagent.libs import centos
from subprocess import Popen, PIPE

from novaagent.libs import DefaultOS


class ServerOS(centos.ServerOS):
    def kmsactivate(self, name, value):
        return kms.kms_activate(value)


if __name__ == '__main__':
    main()
