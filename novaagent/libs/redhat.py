
from __future__ import absolute_import


from novaagent.common import kms
from novaagent.libs import centos


class ServerOS(centos.ServerOS):
    def kmsactivate(self, name, value, client):
        return kms.kms_activate(value)
