
from novaagent import novaagent as agent
from novaagent.libs import centos


import novaagent
import logging
import fcntl
import time
import stat
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


class TestHelpers(TestCase):
    def setUp(self):
        logging.disable(logging.ERROR)

    def tearDown(self):
        logging.disable(logging.NOTSET)
        if os.path.exists('/tmp/.nova-agent.lock'):
            os.remove('/tmp/.nova-agent.lock')

    def setup_lock_file(self):
        lf_path = os.path.join('/tmp', '.nova-agent.lock')
        lf_flags = os.O_WRONLY | os.O_CREAT
        lf_mode = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
        umask_original = os.umask(0)
        try:
            lf_fd = os.open(lf_path, lf_flags, lf_mode)
        finally:
            os.umask(umask_original)

        fcntl.lockf(lf_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def test_xen_action_no_action(self):
        temp_os = centos.ServerOS()
        test_xen_event = {
            "name": "bad_key",
            "value": "68436575764933852815830951574296"
        }
        with mock.patch('novaagent.utils.list_xen_events') as xen_list:
            xen_list.return_value = ['748dee41-c47f-4ec7-b2cd-037e51da4031']
            with mock.patch('novaagent.utils.get_xen_event') as xen_event:
                xen_event.return_value = test_xen_event
                with mock.patch(
                    'novaagent.utils.remove_xenhost_event'
                ) as remove:
                    remove.return_value = True
                    with mock.patch(
                        'novaagent.utils.update_xenguest_event'
                    ) as update:
                        update.return_value = True
                        try:
                            novaagent.novaagent.action(temp_os, 'dummy_client')
                        except:
                            assert False, (
                                'An exception was thrown during action'
                            )

    def test_xen_action_action_success(self):
        temp_os = centos.ServerOS()
        test_xen_event = {
            "name": "keyinit",
            "value": "68436575764933852815830951574296"
        }
        with mock.patch('novaagent.utils.list_xen_events') as xen_list:
            xen_list.return_value = ['748dee41-c47f-4ec7-b2cd-037e51da4031']
            with mock.patch('novaagent.utils.get_xen_event') as xen_event:
                xen_event.return_value = test_xen_event
                with mock.patch('novaagent.libs.DefaultOS.keyinit') as keyinit:
                    keyinit.return_value = ('D0', 'SECRET_STRING')
                    with mock.patch(
                        'novaagent.utils.remove_xenhost_event'
                    ) as remove:
                        remove.return_value = True
                        with mock.patch(
                            'novaagent.utils.update_xenguest_event'
                        ) as update:
                            update.return_value = True
                            try:
                                novaagent.novaagent.action(
                                    temp_os,
                                    'dummy_client'
                                )
                            except:
                                assert False, (
                                    'An exception was thrown during action'
                                )

    def test_main_success(self):
        class Test(object):
            def __init__(self):
                self.logfile = '-'
                self.loglevel = 'info'
                self.no_fork = False

        test_args = Test()
        mock_response = mock.Mock()
        mock_response.side_effect = [
            time.sleep(1),
            time.sleep(1),
            KeyboardInterrupt
        ]
        with mock.patch(
            'novaagent.novaagent.argparse.ArgumentParser.parse_args'
        ) as parse_args:
            parse_args.return_value = test_args
            with mock.patch(
                'novaagent.novaagent.get_server_type'
            ) as server_type:
                server_type.return_value = centos
                with mock.patch('novaagent.novaagent.os.fork') as fork:
                    fork.return_value = 20
                    with mock.patch('novaagent.novaagent.os._exit'):
                        with mock.patch('novaagent.novaagent.action'):
                            with mock.patch(
                                'novaagent.novaagent.os.path.exists'
                            ) as exists:
                                exists.return_value = False
                                with mock.patch(
                                    'novaagent.novaagent.time.sleep',
                                    side_effect=mock_response
                                ):
                                    try:
                                        novaagent.novaagent.main()
                                    except KeyboardInterrupt:
                                        pass
                                    except:
                                        assert False, (
                                            'An unknown exception was thrown'
                                        )

    def test_main_success_no_fork(self):
        class Test(object):
            def __init__(self):
                self.logfile = '-'
                self.loglevel = 'info'
                self.no_fork = True

        test_args = Test()
        mock_response = mock.Mock()
        mock_response.side_effect = [
            time.sleep(1),
            time.sleep(1),
            KeyboardInterrupt
        ]
        with mock.patch(
            'novaagent.novaagent.argparse.ArgumentParser.parse_args'
        ) as parse_args:
            parse_args.return_value = test_args
            with mock.patch(
                'novaagent.novaagent.get_server_type'
            ) as server_type:
                server_type.return_value = centos
                with mock.patch('novaagent.novaagent.action'):
                    with mock.patch(
                        'novaagent.novaagent.os.path.exists'
                    ) as exists:
                        exists.return_value = False
                        with mock.patch(
                            'novaagent.novaagent.time.sleep',
                            side_effect=mock_response
                        ):
                            try:
                                novaagent.novaagent.main()
                            except KeyboardInterrupt:
                                pass
                            except:
                                assert False, 'An unknown exception was thrown'

    def test_main_success_with_xenbus(self):
        class Test(object):
            def __init__(self):
                self.logfile = '-'
                self.loglevel = 'info'
                self.no_fork = False

        test_args = Test()
        mock_response = mock.Mock()
        mock_response.side_effect = [
            time.sleep(1),
            time.sleep(1),
            KeyboardInterrupt
        ]
        with mock.patch(
            'novaagent.novaagent.argparse.ArgumentParser.parse_args'
        ) as parse_args:
            parse_args.return_value = test_args
            with mock.patch(
                'novaagent.novaagent.get_server_type'
            ) as server_type:
                server_type.return_value = centos
                with mock.patch('novaagent.novaagent.os.fork') as fork:
                    fork.return_value = 20
                    with mock.patch('novaagent.novaagent.os._exit'):
                        with mock.patch(
                            'novaagent.novaagent.os.path.exists'
                        ) as exists:
                            exists.return_value = True
                            with mock.patch('novaagent.novaagent.Client'):
                                with mock.patch('novaagent.novaagent.action'):
                                    with mock.patch(
                                        'novaagent.novaagent.time.sleep',
                                        side_effect=mock_response
                                    ):
                                        try:
                                            novaagent.novaagent.main()
                                        except KeyboardInterrupt:
                                            pass
                                        except:
                                            assert False, (
                                                'An unknown exception'
                                                'was thrown'
                                            )

    def test_main_os_error(self):
        class Test(object):
            def __init__(self):
                self.logfile = '-'
                self.loglevel = 'info'
                self.no_fork = False

        test_args = Test()
        mock_response = mock.Mock()
        mock_response.side_effect = [
            True,
            True,
            KeyboardInterrupt
        ]
        with mock.patch(
            'novaagent.novaagent.argparse.ArgumentParser.parse_args'
        ) as parse_args:
            parse_args.return_value = test_args
            with mock.patch(
                'novaagent.novaagent.get_server_type'
            ) as server_type:
                server_type.return_value = centos
                with mock.patch('novaagent.novaagent.os.fork') as fork:
                    fork.side_effect = OSError
                    with mock.patch(
                        'novaagent.novaagent.os._exit',
                        side_effect=OSError
                    ):
                        try:
                            novaagent.novaagent.main()
                        except OSError:
                            pass
                        except:
                            assert False, (
                                'An unknown exception has been thrown on start'
                            )
                        finally:
                            return

    def test_server_type_debian(self):
        mock_response = mock.Mock()
        mock_response.side_effect = [
            False, False, False, False, True
        ]
        with mock.patch(
            'novaagent.novaagent.os.path.exists',
            side_effect=mock_response
        ):
            server_type = novaagent.novaagent.get_server_type()

        self.assertEqual(
            server_type.__name__,
            'novaagent.libs.debian',
            'Did not get expected object for debian'
        )

    def test_server_type_redhat(self):
        mock_response = mock.Mock()
        mock_response.side_effect = [
            False, False, False, True
        ]
        with mock.patch(
            'novaagent.novaagent.os.path.exists',
            side_effect=mock_response
        ):
            server_type = novaagent.novaagent.get_server_type()

        self.assertEqual(
            server_type.__name__,
            'novaagent.libs.redhat',
            'Did not get expected object for redhat'
        )

    def test_server_type_centos(self):
        mock_response = mock.Mock()
        mock_response.side_effect = [
            False, False, True
        ]
        with mock.patch(
            'novaagent.novaagent.os.path.exists',
            side_effect=mock_response
        ):
            server_type = novaagent.novaagent.get_server_type()

        self.assertEqual(
            server_type.__name__,
            'novaagent.libs.centos',
            'Did not get expected object for centos'
        )

    def test_create_lock_file(self):
        agent.create_lock_file()
        self.assertEqual(
            os.path.exists('/tmp/.nova-agent.lock'),
            True,
            'Could not find lock file in expected place'
        )

    def test_create_lock_file_exists(self):
        self.setup_lock_file()
        with mock.patch(
            'novaagent.novaagent.fcntl.lockf',
            side_effect=IOError
        ):
            with mock.patch('novaagent.novaagent.os._exit'):
                novaagent.novaagent.create_lock_file()
