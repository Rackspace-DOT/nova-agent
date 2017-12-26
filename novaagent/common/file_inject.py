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
JSON File injection plugin
"""
from __future__ import print_function


from novaagent.utils import encode_to_bytes
from novaagent.utils import backup_file
from tempfile import mkstemp


import base64
import stat
import os


# This needs to be looked at
def _get_file_permissions(filename):
    try:
        _stat = os.stat(filename)
        return (_stat.st_mode, _stat.st_uid, _stat.st_gid)
    except FileNotFoundError:
        return (None, 0, 0)


def _write_file(filename, data):
    # Get permissions from existing file if it exists
    permission, owner, group = _get_file_permissions(filename)
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    """
    Create temporary file in the directory we want to place the file into

    https://docs.python.org/2/library/tempfile.html
    From the documentation: There are no race conditions in the file’s
    creation, assuming that the platform properly implements the os.O_EXCL
    flag for os.open(). The file is readable and writable only by the
    creating user ID.
    """
    fd, temp_path = mkstemp(dir=dirname, text=True)

    try:
        """
        Set the ownership for the file. If it fails owner/group will be
        root as that is what nova-agent runs under
        """
        os.fchown(fd, owner, group)
    except Exception:
        pass

    try:
        os.fchmod(fd, permission)
    except Exception:
        # If existing file is not found, then set permissions to default 600
        os.fchmod(fd, stat.S_IRUSR | stat.S_IWUSR)

    # Write data to file after all the permissions are set on the temp file
    try:
        os.write(fd, data)
    except TypeError:
        # Python 3 expects bytes so convert and then write to file
        os.write(fd, encode_to_bytes(data))

    os.close(fd)
    # Check for existence of file and back the original up
    if os.path.exists(filename):
        backup_file(filename)

    # Rename the temp file and put in place
    os.rename(temp_path, filename)


class FileInject(object):
    def __init__(self, *args, **kwargs):
        pass

    def injectfile_cmd(self, data):
        try:
            b64_decoded = base64.b64decode(data)
        except Exception:
            return ("500", "Error doing base64 decoding of data")

        filename, data = b64_decoded.decode('utf-8').split(',', 1)
        _write_file(filename, data)
        return ("0", "")
