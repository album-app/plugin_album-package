import inspect
import sys
import os
import re
import tempfile
import unittest.mock
from argparse import Namespace
from unittest import mock
from pathlib import Path
from subprocess import check_output

from album.api import Album
from album.argument_parsing import create_parser
from album.core.api.model.collection_solution import ICollectionSolution
from album.executable import build_executable, create_subscripts_gui, create_subscripts_no_gui, create_spec_file_gui
from album.runner.album_logging import get_active_logger


class TestArgumentParsing(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.album = mock.create_autospec(Album)
        self.resolve_result = mock.create_autospec(ICollectionSolution)
        self.album.resolve.return_value = self.resolve_result
        self.resolve_result.coordinates.return_value = "album:import_unittest:0.1.0"

    @classmethod
    def tearDownClass(cls):
        print("Your Executable Builder works fine.")

    def test_create_parser(self):
        parser = create_parser()
        sys.argv = ["", "package", "1234", "--data_path", "bla", "--output_path", "C:\\Users\\lriecke\\Desktop"]
        args = parser.parse_known_args()
        self.assertEqual("bla", args[0].data_path)
        self.assertEqual("1234", args[0].solution)
        self.assertEqual(False, args[0].no_gui)
        self.assertEqual("C:\\Users\\lriecke\\Desktop", args[0].output_path)
        self.assertEqual(inspect.getsource(build_executable.run), inspect.getsource(args[0].func))

        sys.argv = ["", "package", "1234", "--data_path", "bla", "--output_path",
                    "C:\\Users\\lriecke\\Desktop", "--no_gui"]
        args = parser.parse_known_args()
        self.assertEqual("bla", args[0].data_path)
        self.assertEqual("1234", args[0].solution)
        self.assertEqual(True, args[0].no_gui)
        self.assertEqual("C:\\Users\\lriecke\\Desktop", args[0].output_path)
        self.assertEqual(inspect.getsource(build_executable.run), inspect.getsource(args[0].func))
        # Hier könnte man noch testen ob der gui param richtig behandelt wird sowie der outputpath

    def test_execute_no_gui(self):
        # Testet momentan nur ob eine ausfuehrbare Datei erstellt wird. Koennte noch ein Upgrade vertragen.
        # Wird exe correct ausgefuehrt?

        with tempfile.TemporaryDirectory() as tmpdir:
            build_executable.run(self.album, Namespace(solution=
            Path(os.path.realpath(__file__)).parent.parent.parent.joinpath(
                'src',
                'resources',
                'test_solution',
                'solution.py'),
                output_path=tmpdir,
                data_path="test_data",
                no_gui=True))

            exe_path = Path(tmpdir).joinpath('solution', 'solution.exe')
            check = os.path.isfile(exe_path) and os.access(exe_path, os.X_OK)

            self.assertTrue(check)

    def test_execute_gui(self):
        # Testet momentan nur ob eine ausfuehrbare Datei erstellt wird. Koennte noch ein Upgrade vertragen.
        # Wird exe correct ausgefuehrt?

        with tempfile.TemporaryDirectory() as tmpdir:
            build_executable.run(self.album, Namespace(solution=
            Path(os.path.realpath(__file__)).parent.parent.parent.joinpath(
                'src',
                'resources',
                'test_solution',
                'solution.py'),
                output_path=tmpdir,
                data_path="test_data",
                no_gui=False))

            exe_path = Path(tmpdir).joinpath('solution', 'solution.exe')
            check = os.path.isfile(exe_path) and os.access(exe_path, os.X_OK)

            self.assertTrue(check)

    def test_output_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            build_executable.run(self.album, Namespace(solution=
            Path(os.path.realpath(__file__)).parent.parent.parent.joinpath(
                'src',
                'resources',
                'test_solution',
                'solution.py'),
                output_path=Path(tmpdir).joinpath('test_output'),
                data_path="test_data",
                no_gui=True))

            check = os.path.isdir(Path(tmpdir).joinpath('test_output'))

            self.assertTrue(check)

    def test_no_solution(self):
        with self.assertLogs(get_active_logger(), level='ERROR') as cm:
            with tempfile.TemporaryDirectory() as tmpdir:
                # output_path_var = "C:\\Users\\lriecke\\Desktop\\MDC\\Plugin_Unittests"

                build_executable.run(self.album, Namespace(solution=
                Path(os.path.realpath(__file__)).parent.parent.parent.joinpath(
                    'src',
                    'resources',
                    'test_solution',
                    'murks.py'),
                    output_path=Path(tmpdir).joinpath('test_output'),
                    data_path="test_data",
                    no_gui=True))

        self.assertEqual('ERROR:root:Solution could not be found! Abort.', cm.output[0])

    def test_install_hook_gui(self):
        template_hook_gui = Path(os.path.realpath(__file__)).parent.parent.parent.joinpath('src', 'resources',
                                                                                           'templates',
                                                                                           'gui', 'install_hook.py')
        with tempfile.TemporaryDirectory() as tmpdir:
            create_subscripts_gui.create_hook(tmpdir)
            created_hook_gui = Path(tmpdir).joinpath('install_hook.py')
            created_str = ""
            template_str = ""
            with open(created_hook_gui, 'r') as file:
                created_str = file.read()
            with open(template_hook_gui, 'r') as file:
                template_str = file.read()

            self.assertEqual(template_str, created_str)

    def test_install_hook_no_gui(self):
        template_hook_no_gui = Path(os.path.realpath(__file__)).parent.parent.parent.joinpath('src', 'resources',
                                                                                              'templates',
                                                                                              'no_gui',
                                                                                              'install_hook.py')
        with tempfile.TemporaryDirectory() as tmpdir:
            create_subscripts_no_gui.create_hook(tmpdir)
            created_hook_no_gui = Path(tmpdir).joinpath('install_hook.py')
            created_str = ""
            template_str = ""
            with open(created_hook_no_gui, 'r') as file:
                created_str = file.read()
            with open(template_hook_no_gui, 'r') as file:
                template_str = file.read()

            self.assertEqual(template_str, created_str)

    def test_execute_solution_gui(self):
        template_py_gui = Path(os.path.realpath(__file__)).parent.parent.parent.joinpath('src', 'resources',
                                                                                         'templates',
                                                                                         'gui',
                                                                                         'execute_solution_gui.py')
        with tempfile.TemporaryDirectory() as tmpdir:
            create_subscripts_gui.create_execute_solution(tmpdir)
            created_py_gui = Path(tmpdir).joinpath('execute_solution_gui.py')
            created_str = ""
            template_str = ""
            with open(created_py_gui, 'r') as file:
                created_str = file.read()
            with open(template_py_gui, 'r') as file:
                template_str = file.read()

            self.assertEqual(template_str, created_str)

    def test_clean_up_no_gui(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            build_executable.run(self.album, Namespace(solution=
            Path(os.path.realpath(__file__)).parent.parent.parent.joinpath(
                'src',
                'resources',
                'test_solution',
                'solution.py'),
                output_path=tmpdir,
                data_path="test_data",
                no_gui=True))
            check_1 = os.path.isfile(Path(tmpdir).joinpath('run_solution.py'))
            check_2 = os.path.isfile(Path(tmpdir).joinpath('execute_solution.py'))
            check_3 = os.path.isfile(Path(tmpdir).joinpath('install_hook.py'))
            check_4 = os.path.isfile(Path(tmpdir).joinpath('build_executable.spec'))
            check_5 = os.path.isdir(Path(tmpdir).joinpath('build'))

            self.assertFalse(check_1)
            self.assertFalse(check_2)
            self.assertFalse(check_3)
            self.assertFalse(check_4)
            self.assertFalse(check_5)

    def test_clean_up_gui(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            build_executable.run(self.album, Namespace(solution=
            Path(os.path.realpath(__file__)).parent.parent.parent.joinpath(
                'src',
                'resources',
                'test_solution',
                'solution.py'),
                output_path=tmpdir,
                data_path="test_data",
                no_gui=False))

            check_1 = os.path.isdir(Path(tmpdir).joinpath('build'))
            check_2 = os.path.isfile(Path(tmpdir).joinpath('execute_solution_gui.py'))
            check_3 = os.path.isfile(Path(tmpdir).joinpath('install_hook.py'))
            check_4 = os.path.isfile(Path(tmpdir).joinpath('build_executable_gui.spec'))

            self.assertFalse(check_1)
            self.assertFalse(check_2)
            self.assertFalse(check_3)
            self.assertFalse(check_4)

    # def test_wrong_input(self):
    #    # Das Problem hier ist, dass die exe zwar erstellt wird allerdings kann diese nicht korrekt ausgeführt werden, da
    #    # album dann einen error wirft. Gibt es eine Methode mit der man checken kann ob etwas die solution syntax besitzt


    #
    #    album = mock.create_autospec(Album)
    #    resolve_result = mock.create_autospec(ICollectionSolution)
    #    album.resolve.return_value = resolve_result
    #    resolve_result.coordinates.return_value = "album:import_test:0.1.0"
    #
    #    with self.assertLogs(get_active_logger(), level='ERROR') as cm:
    #        with tempfile.TemporaryDirectory() as tmpdir:
    #            output_path_var = "C:\\Users\\lriecke\\Desktop\\MDC\\Plugin_Unittests"
    #
    #            build_executable.run(album, Namespace(solution=
    #            Path(os.path.realpath(__file__)).parent.parent.parent.joinpath(
    #                'src',
    #                'resources',
    #                'fake_solution',
    #                'solution.py'),
    #                output_path=Path(output_path_var).joinpath('test_output'),
    #                data_path="test_data",
    #                no_gui=True))
    #    self.assertTrue(False)
    # self.assertEqual('ERROR:root:Solution could not be found! Abort.', cm.output[0])


    #def test_execute_solution_no_gui(self):
    #    template_py_no_gui = Path(os.path.realpath(__file__)).parent.parent.parent.joinpath('src', 'resources',
    #                                                                                        'templates',
    #                                                                                        'no_gui',
    #                                                                                        'execute_solution.py')
    #    with tempfile.TemporaryDirectory() as tmpdir:
    #        create_subscripts_no_gui.create_execute_solution(tmpdir)
    #        created_py_no_gui = Path(tmpdir).joinpath('execute_solution.py')
    #        created_str = ""
    #        template_str = ""
    #        with open(created_py_no_gui, 'r') as file:
    #            created_str = file.read()
    #        with open(template_py_no_gui, 'r') as file:
    #            template_str = file.read()
    #        print(created_str)
    #        regex = re.match(r'run_sol_path =[\S\s\w]+[^\n]', created_str)
    #        #start = regex.start()
    #        #end = regex.end()
    #        #span = regex.span()
    #        #print('Start: ' + start)
    #        #print('End: ' + end)
    #        #print('span: ' + span)
    #        print(regex.group(0))
#
    #        self.assertEqual(template_str, created_str)


# def test_spec_file_gui(self):
#    template_spec_gui = Path(os.path.realpath(__file__)).parent.parent.parent.joinpath('src', 'resources',
#                                                                                       'templates',
#                                                                                       'gui',
#                                                                                       'build_executable_gui.spec')
#    with tempfile.TemporaryDirectory() as tmpdir:
#        create_spec_file_gui.run(tmpdir,
#                                 Path(os.path.realpath(__file__)).parent.parent.parent.joinpath('src', 'resources',
#                                                                                                'test_solution',
#                                                                                                'solution.py'))
#        created_spec_gui = Path(tmpdir).joinpath('build_executable_gui.spec')
#        created_str = ""
#        template_str = ""
#        with open(created_spec_gui, 'r') as file:
#            created_str = file.read()
#        with open(template_spec_gui, 'r') as file:
#            template_str = file.read()
#
#        self.assertEqual(template_str, created_str)

# def test_run_solution(self):
#    template_py_no_gui = Path(os.path.realpath(__file__)).parent.parent.parent.joinpath('src', 'resources',
#                                                                                        'templates',
#                                                                                        'no_gui',
#                                                                                        'run_solution.py')
#    with tempfile.TemporaryDirectory() as tmpdir:
#        create_subscripts_no_gui.create_run_solution(tmpdir, "album:import_unittest:0.1.0")
#        created_py_no_gui = Path(tmpdir).joinpath('run_solution.py')
#        created_str = ""
#        template_str = ""
#        with open(created_py_no_gui, 'r') as file:
#            created_str = file.read()
#        with open(template_py_no_gui, 'r') as file:
#            template_str = file.read()
#
#        self.assertEqual(template_str, created_str)

if __name__ == '__main__':
    unittest.main()
