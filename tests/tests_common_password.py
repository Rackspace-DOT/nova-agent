
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
        test = password.PasswordCommands(test='Test Data', test2='Test 2')
        self.assertEqual(
            test.prime,
            162259276829213363391578010288127,
            'Prime values do not match'
        )
        self.assertEqual(
            test.base,
            5,
            'Base values do not match'
        )
        self.assertEqual(
            test.kwargs.get('test'),
            'Test Data',
            "invalid key from kwargs"
        )
        self.assertEqual(
            test.kwargs.get('test2'),
            'Test 2',
            "invalid key from kwargs"
        )

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
        private_key = test._make_private_key()
        self.assertEqual(
            type(private_key),
            long,
            'Invalid return type from make key'
        )

    def test_compute_public_key(self):
        temp_private = 242416858127415443985927051233248666254
        test = password.PasswordCommands()
        public_key = test._dh_compute_public_key(temp_private)
        self.assertEqual(
            type(public_key),
            long,
            'Invalid return type returned from compute public'
        )

    def test_compute_shared_key(self):
        temp_private = 242416858127415443985927051233248666254
        temp_public = 29146890515040234272807524713655
        test = password.PasswordCommands()
        self.assertEqual(
            test._dh_compute_shared_key(temp_private, temp_public),
            158481232637345256609879856716487,
            'Shared key does not match expected value'
        )

    def test_aes_key(self):
        temp_private = '242416858127415443985927051233248666254'
        test_result = (
            b"\xf8\x05\x98\xbb '\xeeM<=\xe2\x8eU\xf6E\xa1",
            b';\xd1\xacR|:\xc2\xdd#t\x181\xad\x11d\x0b'
        )
        test = password.PasswordCommands()
        self.assertEqual(
            test._compute_aes_key(temp_private),
            test_result,
            'AES expected key was not expected value'
        )

    def test_wipe_aes_key(self):
        test = password.PasswordCommands()
        test.aes_key = 'Test Key'
        test._wipe_key()
        try:
            print(test.aes_key)
            assert False, 'AES key was not removed as expected'
        except Exception:
            pass

    def test_wipe_aes_key_error(self):
        test = password.PasswordCommands()
        test._wipe_key()
        try:
            print(test.aes_key)
            assert False, 'AES key was not removed as expected'
        except Exception:
            pass

    def test_key_init(self):
        test = password.PasswordCommands()
        try:
            keyinit = test.keyinit_cmd(242416858127415443985927051233248666254)
        except Exception:
            assert False, 'Key init caused an error'

        self.assertEqual(
            len(keyinit),
            2,
            'Invalid length of return'
        )
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

    def test_change_password_test_mode(self):
        test = password.PasswordCommands(testmode=True)
        self.assertEqual(
            test._change_password('test'),
            None,
            'Return on change in test mode was not None'
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

    def test_decode_password_password_error_length(self):
        temp_pass = base64.b64encode(b'this is a test')
        test = password.PasswordCommands()
        test.aes_key = (
            b"\xf8\x05\x98\xbb '\xeeM<=\xe2\x8eU\xf6E\xa1",
            b';\xd1\xacR|:\xc2\xdd#t\x181\xad\x11d\x0b'
        )
        try:
            test._decode_password(temp_pass)
            assert False, 'Exception was not caught'
        except password.PasswordError as e:
            self.assertEqual(
                str(e),
                "500: Input strings must be a multiple of 16 in length",
                'Incorrect message received generic password error'
            )

    def test_password_cmd_success(self):
        test = password.PasswordCommands(testmode=True)
        test.aes_key = (
            b"\xf8\x05\x98\xbb '\xeeM<=\xe2\x8eU\xf6E\xa1",
            b';\xd1\xacR|:\xc2\xdd#t\x181\xad\x11d\x0b'
        )
        with mock.patch(
            'novaagent.common.password.PasswordCommands._decode_password'
        ):
            with mock.patch(
                'novaagent.common.password.PasswordCommands._change_password'
            ):
                message = test.password_cmd(
                    '6E6haX/YGRSEcR9X9+3nLOgD+ItDTv9/'
                    'uOHms02Cos0sqI/k1uFIC3V/YNydHJOk'
                )

        self.assertEqual(
            ("0", ""),
            message,
            'Did not receive expected message on change password'
        )

    def test_password_cmd_error(self):
        test = password.PasswordCommands(testmode=True)
        message = test.password_cmd('Test Pass')
        self.assertEqual(
            (500, 'Password without key exchange'),
            message,
            'Did not receive expected error on change password'
        )

    def test_password_cmd_invalid_password_data(self):
        test = password.PasswordCommands(testmode=True)
        test.aes_key = (
            b"\xf8\x05\x98\xbb '\xeeM<=\xe2\x8eU\xf6E\xa1",
            b';\xd1\xacR|:\xc2\xdd#t\x181\xad\x11d\x0b'
        )
        message = test.password_cmd(
            "6E6haX/YGRSEcR9X9+3nLOgD+ItDTv9/uOHms02Cos0sqI/k1uFIC3V/YNydHJOk"
        )
        self.assertEqual(
            (500, 'Invalid password data received'),
            message,
            'Did not receive expected error on invalid password data'
        )

    def test_set_password_success(self):
        mock_popen = mock.Mock()
        mock_comm = mock.Mock()
        mock_comm.return_value = 0
        mock_popen.side_effect = [
            mock.Mock(returncode=0, poll=mock_comm)
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

    def test_set_password_success_bytes(self):
        mock_popen = mock.Mock()
        mock_comm = mock.Mock()
        mock_comm.return_value = 0
        mock_stdin = mock.Mock()
        mock_stdin.return_value = [TypeError, None]
        mock_popen.side_effect = [
            mock.Mock(returncode=0, poll=mock_comm, stdin=mock_stdin)
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

    def test_set_password_no_terminate(self):
        mock_popen = mock.Mock()
        mock_comm = mock.Mock()
        mock_comm.return_value = None
        mock_popen.side_effect = [
            mock.Mock(returncode=0, poll=mock_comm)
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
                '500: Failed to change password as passwd '
                'process did not terminate',
                'Invalid message received for failure to terminate'
            )

    def test_set_password_bad_return(self):
        mock_popen = mock.Mock()
        mock_comm = mock.Mock()
        mock_comm.return_value = 0
        mock_popen.side_effect = [
            mock.Mock(returncode=999, poll=mock_comm)
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
                '500: Failed to change password for test: 999',
                'Invalid message received for failure on passwd cmd'
            )
