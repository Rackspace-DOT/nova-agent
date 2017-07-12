
from unittest import TestCase
from novaagent.common import password


import base64
import mock
import glob
import sys
import os


if sys.version_info > (3,):
    long = int


class TestHelpers(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        files = glob.glob('/tmp/passwd*')
        for item in files:
            os.remove(item)

    def setup_test_pw_file(self):
        write_data = [
            'root:$1$p9I3huSF$1acAVn1Kn.DWH1ycSknWR.:17333:0:99999:7:::',
            'bin:*:17110:0:99999:7:::',
            '#daemon:*:17110:0:99999:7:::',
            'thisisabadlineinthepasswordfile',
            'badpass:p9I3huSF$1acAVn1Kn.DWH1ycSknWR.:17113:0:99999:7:::',
            'testuser:$1$p9I3huSF$1acAVn1Kn.DWH1ycSknWR.:17352:0:99999:7:::'
        ]
        with open('/tmp/passwd', 'a+') as f:
            for item in write_data:
                f.write('{0}\n'.format(item))

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
        except:
            pass

    def test_wipe_aes_key_error(self):
        test = password.PasswordCommands()
        test._wipe_key()
        try:
            print(test.aes_key)
            assert False, 'AES key was not removed as expected'
        except:
            pass

    def test_key_init(self):
        test = password.PasswordCommands()
        try:
            keyinit = test.keyinit_cmd(242416858127415443985927051233248666254)
        except:
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

    # Commenting out and will update the tests later
    # def test_decode_password_password_error_bytes(self):
    #     temp_pass = base64.b64encode(b'this is a test')
    #     test = password.PasswordCommands()
    #     test.aes_key = (
    #         b"\xf8\x05\x98\xbb '\xeeM<=\xe2\x8eU\xf6E\xa1",
    #         b';\xd1\xacR|:\xc2\xdd#t\x181\xad\x11d\x0b'
    #     )
    #     try:
    #         test._decode_password(temp_pass)
    #         assert False, 'Exception was not caught'
    #     except password.PasswordError as e:
    #         self.assertEqual(
    #             str(e),
    #             "500: a bytes-like object is required, not 'int'",
    #             'Incorrect message received generic password error'
    #         )

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

    def test_make_salt(self):
        length = 16
        salt_value = password._make_salt(length)
        self.assertEqual(
            len(salt_value),
            length,
            'Invalid salt length'
        )

    def test_create_temp_password_file(self):
        self.setup_test_pw_file()
        temp_file = password._create_temp_password_file(
            'testuser', 'password', '/tmp/passwd'
        )
        self.assertIn(
            '/tmp/passwd',
            temp_file,
            'Did not find original path in temporary file'
        )

    def test_create_temp_password_file_create_salt(self):
        self.setup_test_pw_file()

        temp_file = password._create_temp_password_file(
            'badpass', 'password', '/tmp/passwd'
        )
        self.assertIn(
            '/tmp/passwd',
            temp_file,
            'Did not find original path in temporary file'
        )

    def test_create_temp_password_file_exception(self):
        self.setup_test_pw_file()
        with mock.patch('novaagent.common.password._make_salt') as salt:
            salt.side_effect = ValueError
            try:
                password._create_temp_password_file(
                    'badpass', 'password', '/tmp/passwd'
                )
                assert False, 'Exception should have been raised'
            except Exception:
                pass

    def test_set_password_invalid_file(self):
        password.PASSWD_FILES = ['/tmp/bad_password_file']
        try:
            password.set_password('test', 'test')
            assert False, 'Exception should have been raised'
        except Exception as e:
            self.assertEqual(
                str(e),
                '500: No password file found',
                'Invalid message received for bad file'
            )

    def test_set_password_change_password_success(self):
        self.setup_test_pw_file()
        original_line = (
            'testuser:$1$p9I3huSF$1acAVn1Kn.DWH1ycSknWR.:17352:0:99999:7:::'
        )
        password.PASSWD_FILES = ['/tmp/passwd']
        try:
            password.set_password('testuser', 'test')
        except Exception as e:
            assert False, (
                'Exception raised when should not have: {}'.format(e)
            )

        files = glob.glob('/tmp/passwd*')
        self.assertEqual(len(files), 1, 'Invalid number of files found')
        with open('/tmp/passwd') as f:
            file_data = f.readlines()

        for line in file_data:
            if 'testuser:' in line:
                self.assertNotEqual(
                    line,
                    original_line,
                    'Password was not updated and should have been'
                )
