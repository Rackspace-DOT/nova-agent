
from __future__ import print_function, absolute_import

from novaagent.common import kms

from novaagent.libs import centos


class ServerOS(centos.ServerOS):
    def kmsactivate(self, name, value):
        return kms.kms_activate(value)
