
from novaagent.common import password


import logging
import base64
import glob
import sys
import os


if sys.version_info[:2] >= (2, 7):
    from unittest import TestCase
else:
    from unittest2 import TestCase


try:
    from unittest import mock
except ImportError:
    import mock


if sys.version_info > (3,):
    long = int


class TestHelpers(TestCase):
    def setUp(self):
        logging.disable(logging.ERROR)

    def tearDown(self):
        logging.disable(logging.NOTSET)
        files = glob.glob('/tmp/passwd*')
        for item in files:
            os.remove(item)

    def test_password_error(self):
        test_error = ('000', 'Test Response')
        test = password.PasswordError(test_error)
        self.assertEqual(
            test.__str__(),
            '000: Test Response',
            'Response str did not match expected value'
        )
        self.assertEqual(
            test.get_response(),
            test_error,
            'Response returned did not match expected value'
        )

    def test_password_commands_init(self):
        test = password.PasswordCommands()
        self.assertEqual(
            test.prime,
            162259276829213363391578010288127,
            'Prime values do not match'
        )
        self.assertEqual(test.base, 5, 'Base values do not match')
        self.assertEqual(
            test.min_key_length,
            540,
            "Invalid key length on init"
        )
        self.assertEqual(test._public, None, "Public is not none")
        self.assertEqual(test._private, None, "Private is not none")
        self.assertEqual(test._shared, None, "Shared is not none")
        self.assertEqual(test._aes_key, None, "AES key is not none")
        self.assertEqual(test._aes_iv, None, "AES IV is not none")

    def test_change_password_bytes(self):
        test = password.PasswordCommands()
        test_password = b'test_password\n'
        with mock.patch('novaagent.common.password.set_password'):
            try:
                test._change_password(test_password)
            except Exception:
                assert False, 'An error was generated when should not have'

    def test_change_password_string(self):
        test = password.PasswordCommands()
        test_password = 'test_password\n'
        with mock.patch('novaagent.common.password.set_password'):
            try:
                test._change_password(test_password)
            except Exception:
                assert False, 'An error was generated when should not have'

    def test_make_private_key(self):
        test = password.PasswordCommands()
        test._generate_private_key()
        self.assertEqual(
            type(test._private),
            long,
            'Invalid return type from make key'
        )
        try:
            self.assertGreaterEqual(
                test._private.bit_length(),
                test.min_key_length,
                'Incorrect bit length in private key'
            )
        except AttributeError:
            self.assertGreaterEqual(
                len(bin(test._private)) - 2,
                test.min_key_length,
                'Incorrect bit length in private key'
            )

    def test_compute_public_key(self):
        test = password.PasswordCommands()
        test._generate_private_key()
        test._compute_public_key()
        self.assertEqual(
            type(test._public),
            long,
            'Invalid return type returned from compute public'
        )

    def test_compute_shared_key(self):
        test = password.PasswordCommands()
        test._private = int("""
            23112120562215754241813840772170184083273863303098366811852003357
            72446841869122972713534217535689064137278608958579090107008875567
            5269543831650785847026033312
            46342023613076766721726""".replace('\n', '').replace(' ', ''))

        temp_public = 29146890515040234272807524713655
        test._compute_shared_key(temp_public)
        self.assertEqual(
            test._shared,
            27234591073885988013566387861589,
            'Shared key does not match expected value'
        )

    def test_aes_key(self):
        test = password.PasswordCommands()
        test._compute_aes_key()
        self.assertEqual(
            test._aes_key,
            b'j\xdf\x97\xf8:\xcfdS\xd4\xa6\xa4\xb1\x07\x0f7T',
            'AES key was not expected value'
        )
        self.assertEqual(
            test._aes_iv,
            b'#d\r\xec6\x8f\xbe\xf3\x03dp\xfcTe\xb8e',
            'AES IV set was not expected value'
        )

    def test_clear_data(self):
        test = password.PasswordCommands()
        test._generate_private_key()
        test._compute_public_key()
        test._aes_key = 'Test AES'
        test._aes_iv = 'Test AES IV'
        test._wipe_keys()
        self.assertEqual(test._aes_key, None, "AES key is not None")
        self.assertEqual(test._aes_iv, None, "AES IV is not None")
        self.assertEqual(test._private, None, "Private is not None")
        self.assertEqual(test._public, None, "Public key is not None")
        self.assertEqual(test._shared, None, "Shared key is not None")

    def test_key_init(self):
        test = password.PasswordCommands()
        try:
            keyinit = test.keyinit_cmd(242416858127415443985927051233248666254)
        except Exception:
            assert False, 'Key init caused an error'

        self.assertNotEqual(test._private, None, 'Private is None')
        self.assertNotEqual(test._public, None, 'Public is None')
        self.assertNotEqual(test._shared, None, 'Shared is None')
        self.assertNotEqual(test._aes_key, None, 'AES key is None')
        self.assertNotEqual(test._aes_iv, None, 'AES IV is None')
        self.assertEqual(
            keyinit[0],
            'D0',
            'Unexpected first value of tuple'
        )
        self.assertEqual(
            type(keyinit[1]),
            str,
            'Unexpected type on second value of tuple should be string'
        )

    def test_decode_password_base64_error(self):
        test = password.PasswordCommands()
        try:
            test._decode_password(password)
            assert False, 'Exception was not caught'
        except password.PasswordError as e:
            self.assertEqual(
                str(e),
                "500: Couldn't decode base64 data",
                'Incorrect message received on exception'
            )

    def test_decode_password_no_key_exchange(self):
        temp_pass = base64.b64encode(b'this is a test')
        test = password.PasswordCommands()
        try:
            test._decode_password(temp_pass)
            assert False, 'Exception was not caught'
        except password.PasswordError as e:
            self.assertEqual(
                str(e),
                "500: Password without key exchange",
                'Incorrect message received on AES error'
            )

    def test_decode_password_password_exception(self):
        temp_pass = base64.b64encode(b'this is a test')
        test = password.PasswordCommands()
        test._compute_aes_key()
        password_error = password.PasswordError((999, "Generate Exception"))
        with mock.patch(
            'novaagent.common.password.PasswordCommands._decrypt_password',
            side_effect=password_error
        ):
            try:
                test._decode_password(temp_pass)
                assert False, 'A PasswordError exception shouldhave occurred'
            except password.PasswordError:
                pass
            except Exception:
                assert False, 'PasswordError exception was not triggered'

    def test_decode_password_general_exception(self):
        temp_pass = base64.b64encode(b'this is a test')
        test = password.PasswordCommands()
        test._compute_aes_key()
        with mock.patch(
            'novaagent.common.password.PasswordCommands._decrypt_password',
            side_effect=ValueError('This is a test')
        ):
            try:
                test._decode_password(temp_pass)
                assert False, 'A PasswordError should have occurred'
            except password.PasswordError:
                pass
            except Exception:
                assert False, 'A PasswordError should have been raised'

    def test_decode_password_success(self):
        temp_pass = base64.b64encode(b'this is a test')
        test = password.PasswordCommands()
        test._compute_aes_key()
        with mock.patch(
            'novaagent.common.password.PasswordCommands._decrypt_password',
        ) as decrypt:
            decrypt.return_value = 'test_password'
            try:
                returned_password = test._decode_password(temp_pass)
            except Exception:
                assert False, 'An exception occurred and should not have'

        self.assertEqual(
            returned_password,
            'test_password',
            'Password returned does not match'
        )

    def test_decode_password_password_error_length(self):
        temp_pass = base64.b64encode(b'this is a test')
        test = password.PasswordCommands()
        test._aes_key = b"\xf8\x05\x98\xbb '\xeeM<=\xe2\x8eU\xf6E\xa1"
        test._aes_iv = b';\xd1\xacR|:\xc2\xdd#t\x181\xad\x11d\x0b'
        try:
            test._decode_password(temp_pass)
            assert False, 'Exception was not caught'
        except password.PasswordError as e:
            self.assertEqual(
                str(e),
                "500: Input strings must be a multiple of 16 in length",
                'Incorrect message received generic password error'
            )

    def test_password_cmd_invalid_password_data(self):
        test = password.PasswordCommands()
        test._aes_key = b"\xf8\x05\x98\xbb '\xeeM<=\xe2\x8eU\xf6E\xa1"
        test._aes_iv = b';\xd1\xacR|:\xc2\xdd#t\x181\xad\x11d\x0b'
        message = test.password_cmd(
            "6E6haX/YGRSEcR9X9+3nLOgD+ItDTv9/uOHms02Cos0sqI/k1uFIC3V/YNydHJOk"
        )
        self.assertEqual(
            (500, 'Invalid password data received'),
            message,
            'Did not receive expected error on invalid password data'
        )

    def test_password_cmd_success(self):
        test = password.PasswordCommands()
        test._aes_key = 'AES Key'
        test._aes_iv = 'AES IV'
        test._private = 'Private'
        test._shared = 'Shared'
        test._public = 'Public'
        with mock.patch(
            'novaagent.common.password.PasswordCommands._decode_password'
        ) as decode:
            decode.return_value = 'test'
            with mock.patch(
                'novaagent.common.password.PasswordCommands._change_password'
            ):
                message = test.password_cmd(
                    '6E6haX/YGRSEcR9X9+3nLOgD+ItDTv9/'
                    'uOHms02Cos0sqI/k1uFIC3V/YNydHJOk'
                )

        self.assertEqual(test._aes_key, None, "AES key is not None")
        self.assertEqual(test._aes_iv, None, "AES IV is not None")
        self.assertEqual(test._private, None, "Private is not None")
        self.assertEqual(test._public, None, "Public key is not None")
        self.assertEqual(test._shared, None, "Shared key is not None")
        self.assertEqual(
            ("0", ""),
            message,
            'Did not receive expected message on change password'
        )

    def test_password_cmd_error(self):
        test = password.PasswordCommands()
        password_error = password.PasswordError((999, "Generate Exception"))
        with mock.patch(
            'novaagent.common.password.PasswordCommands._decode_password',
            side_effect=password_error
        ):
            message = test.password_cmd('Test Pass')

        self.assertEqual(
            (999, "Generate Exception"),
            message,
            'Did not receive expected message on change password exception'
        )

    def test_set_password_success(self):
        mock_popen = mock.Mock()
        mock_comm = mock.Mock()
        mock_comm.return_value = ('out', 'error')
        mock_popen.side_effect = [
            mock.Mock(returncode=0, communicate=mock_comm)
        ]
        try:
            with mock.patch(
                'novaagent.common.password.Popen',
                side_effect=mock_popen
            ):
                password.set_password('test', 'test')
        except Exception:
            assert False, 'Exception should not have been raised'

    def test_set_password_success_bytes(self):
        mock_popen = mock.Mock()
        mock_comm = mock.Mock()
        mock_comm.return_value = ('out', 'error')
        mock_stdin = mock.Mock()
        mock_stdin.write.side_effect = [TypeError(), None]
        mock_popen.side_effect = [
            mock.Mock(returncode=0, communicate=mock_comm, stdin=mock_stdin)
        ]
        try:
            with mock.patch(
                'novaagent.common.password.Popen',
                side_effect=mock_popen
            ):
                returned = password.set_password('test', 'test')

            self.assertEqual(returned, None, 'Invalid return value on success')
        except Exception:
            assert False, 'Exception should not have been raised'

    def test_set_password_success_string(self):
        mock_popen = mock.Mock()
        mock_comm = mock.Mock()
        mock_comm.return_value = ('out', 'error')
        mock_stdin = mock.Mock()
        mock_stdin.side_effect = [None]
        mock_popen.side_effect = [
            mock.Mock(returncode=0, communicate=mock_comm, stdin=mock_stdin)
        ]
        try:
            with mock.patch(
                'novaagent.common.password.Popen',
                side_effect=mock_popen
            ):
                returned = password.set_password('test', 'test')

            self.assertEqual(returned, None, 'Invalid return value on success')
        except Exception:
            assert False, 'Exception should not have been raised'

    def test_set_password_bad_return(self):
        mock_popen = mock.Mock()
        mock_comm = mock.Mock()
        mock_comm.return_value = ('out', 'error')
        mock_popen.side_effect = [
            mock.Mock(returncode=999, communicate=mock_comm)
        ]
        try:
            with mock.patch(
                'novaagent.common.password.Popen',
                side_effect=mock_popen
            ):
                password.set_password('test', 'test')

            assert False, 'Exception should have been raised'
        except Exception as e:
            self.assertEqual(
                str(e),
                '500: Failed to change password for test: 999 : error',
                'Invalid message received for failure on passwd cmd'
            )
