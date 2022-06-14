import inspect
import os
import platform
import re
import sys
import unittest.mock
from pathlib import Path

import pkg_resources

from album.argument_parsing import create_parser
from album.package import build_executable, create_subscripts_gui, create_subscripts_no_gui, create_spec_file_gui, \
    create_spec_file_no_gui
from test_package.test_common import TestCommon


class TestUnitBuildExecutable(TestCommon):

    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_create_parser(self):
        parser = create_parser()
        sys.argv = ["", "package", "1234", "--output_path", "An_example_path"]
        args = parser.parse_known_args()
        self.assertEqual("1234", args[0].solution)
        self.assertEqual(False, args[0].no_gui)
        self.assertEqual("An_example_path", args[0].output_path)
        self.assertEqual(inspect.getsource(build_executable.run), inspect.getsource(args[0].func))

        sys.argv = ["", "package", "1234", "--output_path",
                    "An_example_path", "--no_gui"]
        args = parser.parse_known_args()
        self.assertEqual("1234", args[0].solution)
        self.assertEqual(True, args[0].no_gui)
        self.assertEqual("An_example_path", args[0].output_path)
        self.assertEqual(inspect.getsource(build_executable.run), inspect.getsource(args[0].func))

    def test_call_solution_gui(self):
        template_py_gui = Path(os.path.realpath(__file__)).parent.parent.parent.joinpath('test_package', 'resources',
                                                                                         'templates',
                                                                                         'gui',
                                                                                         'call_solution_gui.py')
        create_subscripts_gui.create_call_solution(self.tmp_dir.name)
        created_py_gui = Path(self.tmp_dir.name).joinpath('call_solution_gui.py')

        with open(created_py_gui, 'r') as file:
            created_str = file.read()
        with open(template_py_gui, 'r') as file:
            template_str = file.read()

        self.assertEqual(template_str, created_str)

    def test_call_solution_no_gui(self):
        template_py_no_gui = Path(os.path.realpath(__file__)).parent.parent.parent.joinpath('test_package', 'resources',
                                                                                            'templates',
                                                                                            'no_gui',
                                                                                            'call_solution.py')
        create_subscripts_no_gui.create_call_solution(self.tmp_dir.name)
        created_py_no_gui = Path(self.tmp_dir.name).joinpath('call_solution.py')
        created_str = ""
        template_str = ""
        with open(created_py_no_gui, 'r') as file:
            created_str = file.read()
        with open(template_py_no_gui, 'r') as file:
            template_str = file.read()

        self.assertEqual(template_str, created_str)

    def test_spec_file_gui(self):
        template_spec_gui = Path(os.path.realpath(__file__)).parent.parent.parent.joinpath('test_package', 'resources',
                                                                                           'templates', 'gui',
                                                                                           'build_executable_gui.spec')


        create_spec_file_gui.create(self.tmp_dir.name,
                                 Path(os.path.realpath(__file__)).parent.parent.parent.joinpath('test_package',
                                                                                                'resources',
                                                                                                'test_solution',
                                                                                                'solution.py'))
        created_spec_gui = Path(self.tmp_dir.name).joinpath('build_executable_gui.spec')


        #install_script_path = repr(str(pkg_resources.resource_filename('album.package.resources','install_all.py')))
        yml_path = repr(str(Path(self.tmp_dir.name).joinpath('album.yml')))

        test_solution_path = repr(
            str(Path(os.path.realpath(__file__)).parent.parent.joinpath('resources', 'test_solution', '*.py')))
        hook_path = repr(str(pkg_resources.resource_filename('album.package.resources', 'install_all.py')))
        created_str = ""
        template_str = ""
        with open(created_spec_gui, 'r') as file:
            created_str = file.read()
        with open(template_spec_gui, 'r') as file:
            template_str = file.read()

        tmp = re.sub(r"\\", r"\\\\", yml_path)
        template_str = re.sub("<yml_path>", tmp, template_str)
        tmp = re.sub(r"\\", r"\\\\", test_solution_path)
        template_str = re.sub("<test_solution_path>", tmp, template_str)
        tmp = re.sub(r"\\", r"\\\\", hook_path)
        template_str = re.sub("<hook_path>", tmp, template_str)
        self.maxDiff = None
        self.assertEqual(template_str, created_str)

    def test_spec_file_no_gui(self):
        template_spec_no_gui = Path(os.path.realpath(__file__)).parent.parent.parent.joinpath('test_package',
                                                                                              'resources',
                                                                                              'templates', 'no_gui',
                                                                                              'build_executable.spec')

        create_spec_file_no_gui.create(self.tmp_dir.name,
                                    Path(os.path.realpath(__file__)).parent.parent.parent.joinpath('test_package',
                                                                                                   'resources',
                                                                                                   'test_solution',
                                                                                                   'solution.py'))

        created_spec_no_gui = Path(self.tmp_dir.name).joinpath('build_executable.spec')

        if platform.system() == 'Windows':
            install_script_path = repr(str(pkg_resources.resource_filename('album.package.resources','install_album_win64.bat')))
        elif platform.system() == 'Darwin':
            install_script_path = repr(str(pkg_resources.resource_filename('album.package.resources','install_album_macos.sh')))
        elif platform.system() == 'Linux':
            install_script_path = repr(str(pkg_resources.resource_filename('album.package.resources','install_album_linux64.sh')))
        else:
            raise NotImplementedError

        test_solution_path = repr(
            str(Path(os.path.realpath(__file__)).parent.parent.joinpath('resources', 'test_solution', '*')))
        hook_path = repr(str(Path(self.tmp_dir.name).joinpath('install_hook.py')))
        run_solution_path = repr(str(Path(self.tmp_dir.name).joinpath('run_solution.py')))

        created_str = ""
        template_str = ""
        with open(created_spec_no_gui, 'r') as file:
            created_str = file.read()
        with open(template_spec_no_gui, 'r') as file:
            template_str = file.read()

        tmp = re.sub(r"\\", r"\\\\", install_script_path)
        template_str = re.sub("<install_script_path>", tmp, template_str)
        tmp = re.sub(r"\\", r"\\\\", test_solution_path)
        template_str = re.sub("<test_solution_path>", tmp, template_str)
        tmp = re.sub(r"\\", r"\\\\", hook_path)
        template_str = re.sub("<hook_path>", tmp, template_str)
        tmp = re.sub(r"\\", r"\\\\", run_solution_path)
        template_str = re.sub("<run_solution_path>", tmp, template_str)
        self.maxDiff = None
        self.assertEqual(template_str, created_str)

    def test_run_solution(self):
        template_py_no_gui = Path(os.path.realpath(__file__)).parent.parent.parent.joinpath('test_package', 'resources',
                                                                                            'templates',
                                                                                            'no_gui',
                                                                                            'run_solution_template.py')
        create_subscripts_no_gui.create_run_solution(self.tmp_dir.name, "album:import_unittest:0.1.0")
        created_py_no_gui = Path(self.tmp_dir.name).joinpath('run_solution.py')
        with open(created_py_no_gui, 'r') as file:
            created_str = file.read()
        with open(template_py_no_gui, 'r') as file:
            template_str = file.read()
        # tmp construct is needed since the re.sub command deescapse a path string from something like C:\\.. to C:\..
        tmp = re.sub(r"\\", r"\\\\", repr(str(Path.home().joinpath('.album', 'env', 'album'))))
        template_str = re.sub("\"<base_path>\"", tmp,
                              template_str)
        self.assertEqual(template_str, created_str)


if __name__ == '__main__':
    unittest.main()
