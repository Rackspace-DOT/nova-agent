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

from subprocess import PIPE
from subprocess import Popen


import binascii
import base64
import sys
import os


from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends.openssl.backend import backend


if sys.version_info > (3,):
    long = int


# This is to support older python versions that don't have hashlib
try:
    import hashlib
except ImportError:
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
    def __init__(self):
        self.prime = 162259276829213363391578010288127
        self.base = 5
        self.min_key_length = 540
        self._public = None
        self._private = None
        self._shared = None
        self._aes_key = None
        self._aes_iv = None

    def _generate_private_key(self):
        """Create a private key using /dev/urandom"""
        _bytes = self.min_key_length // 8 + 8
        self._private = int(binascii.hexlify(os.urandom(_bytes)), 16)

    def _compute_public_key(self):
        """Given a private key, compute a public key"""
        self._public = pow(self.base, self._private, self.prime)

    def _compute_shared_key(self, remote_public_key):
        """Given public and private keys, compute the shared key"""
        self._shared = pow(remote_public_key, self._private, self.prime)

    def _compute_aes_key(self):
        """
        Given a key, compute the corresponding key that can be used
        with AES
        """
        shared_string = str(self._shared)
        self._aes_key = (hashlib.md5(shared_string.encode('utf-8'))).digest()

        m = hashlib.md5(self._aes_key)
        m.update(shared_string.encode('utf-8'))
        self._aes_iv = m.digest()

    def _decrypt_password(self, data):
        try:
            # Version 3 or later
            cipher = Cipher(algorithms.AES(self._aes_key),
                            modes.CBC(self._aes_iv),
                            backend=backend)
        except Exception:
            # Previous to version 3
            cipher = Cipher(algorithms.AES(self._aes_key),
                            modes.CBC(self._aes_iv),
                            backend)

        decryptor = cipher.decryptor()
        decrypted_passwd = decryptor.update(data) + decryptor.finalize()
        # aes = pyaes.AESModeOfOperationCBC(self._aes_key, iv=self._aes_iv)
        # decrypted_passwd = aes.decrypt(data)
        try:
            cut_off_sz = ord(decrypted_passwd[len(decrypted_passwd) - 1])
        except Exception:
            cut_off_sz = decrypted_passwd[len(decrypted_passwd) - 1]

        if cut_off_sz > 16 or len(decrypted_passwd) < 16:
            raise PasswordError((500, "Invalid password data received"))

        passwd = decrypted_passwd[: - cut_off_sz]
        return passwd

    def _decode_password(self, data):
        try:
            real_data = base64.b64decode(data)
        except Exception:
            raise PasswordError((500, "Couldn't decode base64 data"))

        if self._aes_key is None:
            raise PasswordError((500, "Password without key exchange"))

        try:
            passwd = self._decrypt_password(real_data)
        except PasswordError as exc:
            raise exc
        except Exception as exc:
            raise PasswordError((500, str(exc)))

        return passwd

    def _change_password(self, passwd):
        if isinstance(passwd, bytes):
            string_passwd = passwd.decode('utf-8')
        else:
            string_passwd = str(passwd)

        # Make sure there are no newlines at the end
        set_password('root', string_passwd.strip('\n'))

    def _wipe_keys(self):
        """
        Reset Values from previous keyinit command as each password keyinit is
        called again and new values are generated
        """
        self._aes_key = None
        self._aes_iv = None
        self._private = None
        self._public = None
        self._shared = None

    def keyinit_cmd(self, data):
        """
        Remote public key should come in as a large number. Set it to long in
        case it comes in as a string
        """
        remote_public_key = long(data)

        # Sets self._private
        self._generate_private_key()

        # Sets self._public
        self._compute_public_key()

        # Sets self._shared
        self._compute_shared_key(remote_public_key)

        # Sets self._aes_key and self._aes_iv
        self._compute_aes_key()

        # Return the public key as a string
        return ("D0", str(self._public))

    def password_cmd(self, data):
        try:
            passwd = self._decode_password(data)
            self._change_password(passwd)
        except PasswordError as exc:
            return exc.get_response()

        self._wipe_keys()
        return ("0", "")


def set_password(user, password):
    """Set the password for a particular user using passwd"""
    p = Popen(
        ['passwd', user],
        stdout=PIPE,
        stderr=PIPE,
        stdin=PIPE
    )
    try:
        p.stdin.write(u'{0}\n{0}\n'.format(password))
    except TypeError:
        # Python 3 wants bytes so catch the exception and encode properly
        p.stdin.write(u'{0}\n{0}\n'.format(password).encode('utf-8'))

    p.stdin.flush()
    out, err = p.communicate()
    if p.returncode != 0:
        raise PasswordError(
            (
                500,
                'Failed to change password for {0}: {1} : {2}'.format(
                    user,
                    p.returncode,
                    err
                )
            )
        )

    return
