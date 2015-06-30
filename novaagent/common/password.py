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
JSON password reset handling plugin
"""

import base64
import binascii
import logging
import sys
import os
import subprocess
import time

from Crypto.Cipher import AES

if sys.version_info > (3,):
    long = int

# This is to support older python versions that don't have hashlib
try:
    import hashlib
except ImportError as exc:
    import md5

    class hashlib(object):
        """Fake hashlib module as a class"""

        @staticmethod
        def md5():
            return md5.new()


class PasswordError(Exception):
    """
    Class for password command exceptions
    """

    def __init__(self, response):
        # Should be a (ResponseCode, ResponseMessage) tuple
        self.response = response

    def __str__(self):
        return "%s: %s" % self.response

    def get_response(self):
        return self.response


class PasswordCommands(object):
    """
    Class for password related commands
    """

    def __init__(self, *args, **kwargs):
        # prime to use
        self.prime = 162259276829213363391578010288127
        self.base = 5
        self.kwargs = {}
        self.kwargs.update(kwargs)

    def _mod_exp(self, num, exp, mod):
        result = 1
        while exp > 0:
            if (exp & 1) == 1:
                result = (result * num) % mod
            exp = exp >> 1
            num = (num * num) % mod
        return result

    def _make_private_key(self):
        """
        Create a private key using /dev/urandom
        """

        return int(binascii.hexlify(os.urandom(16)), 16)

    def _dh_compute_public_key(self, private_key):
        """
        Given a private key, compute a public key
        """

        return self._mod_exp(self.base, private_key, self.prime)

    def _dh_compute_shared_key(self, public_key, private_key):
        """
        Given public and private keys, compute the shared key
        """

        return self._mod_exp(public_key, private_key, self.prime)

    def _compute_aes_key(self, key):
        """
        Given a key, compute the corresponding key that can be used
        with AES
        """

        m = hashlib.md5()
        m.update(key.encode('utf-8'))

        aes_key = m.digest()

        m = hashlib.md5()
        m.update(aes_key)
        m.update(key.encode('utf-8'))

        aes_iv = m.digest()

        return (aes_key, aes_iv)

    def _decrypt_password(self, aes_key, data):

        aes = AES.new(aes_key[0], AES.MODE_CBC, aes_key[1])
        passwd = aes.decrypt(data)

        cut_off_sz = ord(passwd[len(passwd) - 1])
        if cut_off_sz > 16 or len(passwd) < 16:
            raise PasswordError((500, "Invalid password data received"))

        passwd = passwd[: - cut_off_sz]

        return passwd

    def _decode_password(self, data):

        try:
            real_data = base64.b64decode(data)
        except Exception as exc:
            raise PasswordError((500, "Couldn't decode base64 data"))

        try:
            aes_key = self.aes_key
        except AttributeError as exc:
            raise PasswordError((500, "Password without key exchange"))

        try:
            passwd = self._decrypt_password(aes_key, real_data)
        except PasswordError as exc:
            raise exc
        except Exception as exc:
            raise PasswordError((500, str(exc)))

        return passwd

    def _change_password(self, passwd):
        """Actually change the password"""

        if self.kwargs.get('testmode', False):
            return None
        # Make sure there are no newlines at the end
        set_password('root', passwd.strip('\n'))

    def _wipe_key(self):
        """
        Remove key from a previous keyinit command
        """

        try:
            del self.aes_key
        except AttributeError as exc:
            pass

    def keyinit_cmd(self, data):

        # Remote pubkey comes in as large number

        # Or well, it should come in as a large number.  It's possible
        # that some legacy client code will send it as a string.  So,
        # we'll make sure to always convert it to long.
        remote_public_key = long(data)

        my_private_key = self._make_private_key()
        my_public_key = self._dh_compute_public_key(my_private_key)

        shared_key = str(self._dh_compute_shared_key(remote_public_key,
                my_private_key))

        self.aes_key = self._compute_aes_key(shared_key)

        # The key needs to be a string response right now
        return ("D0", str(my_public_key))

    def password_cmd(self, data):

        try:
            passwd = self._decode_password(data)
            self._change_password(passwd)
        except PasswordError as exc:
            return exc.get_response()

        self._wipe_key()

        return (0, "")


def _make_salt(length):
    """Create a salt of appropriate length"""

    salt_chars = 'abcdefghijklmnopqrstuvwxyz'
    salt_chars += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    salt_chars += '0123456789./'

    rand_data = os.urandom(length)
    salt = ''
    for c in rand_data:
        salt += salt_chars[ord(c) % len(salt_chars)]
    return salt


def _create_temp_password_file(user, password, filename):
    """Read original passwd file, generating a new temporary file.

    Returns: The temporary filename
    """

    with open(filename) as f:
        file_data = f.readlines()
    stat_info = os.stat(filename)
    tmpfile = '%s.tmp.%d' % (filename, os.getpid())

    # We have to use os.open() so that we can create the file with
    # the appropriate modes.  If we create it and set modes later,
    # there's a small point of time where a non-root user could
    # potentially open the file and wait for data to be written.
    fd = os.open(tmpfile,
            os.O_CREAT | os.O_TRUNC | os.O_WRONLY,
            stat_info.st_mode)
    f = None
    success = False
    try:
        os.chown(tmpfile, stat_info.st_uid, stat_info.st_gid)
        f = os.fdopen(fd, 'w')
        for line in file_data:
            if line.startswith('#'):
                f.write(line)
                continue
            try:
                (s_user, s_password, s_rest) = line.split(':', 2)
            except ValueError as exc:
                f.write(line)
                continue
            if s_user != user:
                f.write(line)
                continue
            if s_password.startswith('$'):
                # Format is '$ID$SALT$HASH' where ID defines the
                # ecnryption type.  We'll re-use that, and make a salt
                # that's the same size as the old
                salt_data = s_password[1:].split('$')
                salt = '$%s$%s$' % (salt_data[0],
                        _make_salt(len(salt_data[1])))
            else:
                # Default to MD5 as a minimum level of compatibility
                salt = '$1$%s$' % _make_salt(8)
            enc_pass = agentlib.encrypt_password(password, salt)
            f.write("%s:%s:%s" % (s_user, enc_pass, s_rest))
        f.close()
        f = None
        success = True
    except Exception as exc:
        logging.error("Couldn't create temporary password file: %s" % str(e))
        raise
    finally:
        if not success:
            # Close the file if it's open
            if f:
                try:
                    os.unlink(tmpfile)
                except Exception as exc:
                    pass
            # Make sure to unlink the tmpfile
            try:
                os.unlink(tmpfile)
            except Exception as exc:
                pass

    return tmpfile


def set_password(user, password):
    """Set the password for a particular user"""

    INVALID = 0
    PWD_MKDB = 1
    RENAME = 2

    files_to_try = {'/etc/shadow': RENAME,
            '/etc/master.passwd': PWD_MKDB}

    for filename, ftype in files_to_try.iteritems():
        if not os.path.exists(filename):
            continue
        tmpfile = _create_temp_password_file(user, password, filename)
        if ftype == RENAME:
            bakfile = '/etc/shadow.bak.%d' % os.getpid()
            os.rename(filename, bakfile)
            os.rename(tmpfile, filename)
            os.remove(bakfile)
            return
        if ftype == PWD_MKDB:
            pipe = subprocess.PIPE
            p = subprocess.Popen(['/usr/sbin/pwd_mkdb', tmpfile],
                    stdin=pipe, stdout=pipe, stderr=pipe)
            (stdoutdata, stderrdata) = p.communicate()
            if p.returncode != 0:
                if stderrdata:
                    stderrdata.strip('\n')
                else:
                    stderrdata = '<None>'
                logging.error("pwd_mkdb failed: %s" % stderrdata)
                try:
                    os.unlink(tmpfile)
                except Exception as exc:
                    pass
                raise PasswordError(
                        (500, "Rebuilding the passwd database failed"))
            return
    raise PasswordError((500, "Unknown password file format"))
