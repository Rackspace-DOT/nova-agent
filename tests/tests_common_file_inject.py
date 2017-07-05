
from unittest import TestCase
from novaagent.common import file_inject


import base64
import shutil
import glob
import os


class TestHelpers(TestCase):
    def setUp(self):
        if not os.path.exists('/tmp/test_file'):
            with open('/tmp/test_file', 'a+') as f:
                f.write('This is a test file')
                os.utime('/tmp/test_file', None)

    def tearDown(self):
        files = glob.glob('/tmp/test_file*')
        for item in files:
            os.remove(item)

        try:
            shutil.rmtree('/tmp/tests')
        except:
            pass

    def test_file_permission(self):
        mode, uid, gid = file_inject._get_file_permissions('/tmp/test_file')
        self.assertEqual(mode, 33188, 'Mode is not expected value')
        self.assertEqual(uid, 501, 'UID is not expected value')
        self.assertEqual(gid, 0, 'GID is not expected value')

    def test_file_permission_exception(self):
        os.remove('/tmp/test_file')
        mode, uid, gid = file_inject._get_file_permissions('/tmp/test_file')
        self.assertEqual(mode, 0o644, 'Mode is not expected value')
        self.assertEqual(uid, 0, 'UID is not expected value')
        self.assertEqual(gid, 0, 'GID is not expected value')

    def test_write_file(self):
        file_inject._write_file(
            '/tmp/test_file_write',
            'File Contents'
        )
        files = glob.glob('/tmp/test_file*')
        self.assertEqual(
            len(files),
            2,
            'Did not find any files'
        )
        found_file = False
        temp_contents = None
        for f in files:
            if '/tmp/test_file_write' == f:
                with open(f) as temp_file:
                    temp_contents = temp_file.read()

                found_file = True

        assert found_file, 'Did not find written file in expected path'
        self.assertEqual(
            temp_contents,
            'File Contents',
            'Written data in file is not what was expected'
        )

    def test_write_file_existing_file(self):
        file_inject._write_file(
            '/tmp/test_file',
            'File Contents'
        )
        files = glob.glob('/tmp/test_file*')
        self.assertEqual(
            len(files),
            2,
            'Did not find any files'
        )
        found_file = False
        temp_contents = None
        for f in files:
            if '/tmp/test_file' == f:
                with open(f) as temp_file:
                    temp_contents = temp_file.read()

                found_file = True

        assert found_file, 'Did not find written file in expected path'
        self.assertEqual(
            temp_contents,
            'File Contents',
            'Written data in file is not what was expected'
        )

    def test_instantiate_file_inject(self):
        file_inject.FileInject()
        assert True, 'Class did not generate exception'

    def test_inject_file_cmd(self):
        test = file_inject.FileInject()
        encode_details = base64.b64encode(
            b'/tmp/tests/test_file_write,Testing the inject'
        )
        error, message = test.injectfile_cmd(encode_details)
        self.assertEqual(error, "0", "Did not get expected error code")
        self.assertEqual(
            message,
            "",
            "Did not get expected message on success"
        )
        files = glob.glob('/tmp/tests/test_file*')
        self.assertEqual(
            len(files),
            1,
            'Did not find any files'
        )
        found_file = False
        temp_contents = None
        for f in files:
            if '/tmp/tests/test_file_write' == f:
                with open(f) as temp_file:
                    temp_contents = temp_file.read()

                found_file = True

        assert found_file, 'Did not find written file in expected path'
        self.assertEqual(
            temp_contents,
            'Testing the inject',
            'Written data in file is not what was expected'
        )

    def test_inject_file_cmd_exception(self):
        test = file_inject.FileInject()
        error, message = test.injectfile_cmd('Unencoded data')
        self.assertEqual(error, "500", "Did not get expected error code")
        self.assertEqual(
            message,
            "Error doing base64 decoding of data",
            "Did not get expected message on error"
        )
