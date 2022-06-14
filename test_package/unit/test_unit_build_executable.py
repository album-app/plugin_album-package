import inspect
import os
import sys
import unittest.mock
from pathlib import Path

import pkg_resources

from album import core
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
        create_subscripts_gui.create_call_solution(self.tmp_dir.name)
        self.assertTrue(os.path.isfile(Path(self.tmp_dir.name).joinpath('call_solution_gui.py')))

    def test_call_solution_no_gui(self):
        create_subscripts_no_gui.create_call_solution(self.tmp_dir.name)
        self.assertTrue(os.path.isfile(Path(self.tmp_dir.name).joinpath('call_solution.py')))

    def test_spec_file_gui(self):
        yml_path = repr(str(Path(self.tmp_dir.name).joinpath('album.yml')))
        test_solution_path = repr(
            str(Path(os.path.realpath(__file__)).parent.parent.joinpath('resources', 'test_solution', '*.py')))
        hook_path = repr(str(pkg_resources.resource_filename('album.package.resources', 'install_all.py')))

        datas_string = "\t\t\t datas=[(%s, '.'),(%s, 'solution_files')],\n" % (yml_path, test_solution_path)
        hook_string = "\t\t\t runtime_hooks=[%s],\n" % hook_path

        create_spec_file_gui.create(self.tmp_dir.name,
                                    Path(os.path.realpath(__file__)).parent.parent.parent.joinpath('test_package',
                                                                                                   'resources',
                                                                                                   'test_solution',
                                                                                                   'solution.py'))
        created_spec_gui = Path(self.tmp_dir.name).joinpath('build_executable_gui.spec')

        counter = 0
        with open(created_spec_gui, 'r') as file:
            for line in file:
                if line.startswith("\t\t\t datas="):
                    data_line = line
                    counter += 1
                if line.startswith("\t\t\t runtime_hooks="):
                    hook_line = line
                    counter += 1

        self.assertTrue(os.path.isfile(created_spec_gui))
        self.assertEqual(datas_string, data_line)
        self.assertEqual(hook_string, hook_line)
        self.assertEqual(counter, 2)

    def test_spec_file_no_gui(self):
        yml_path = repr(str(Path(self.tmp_dir.name).joinpath('album.yml')))
        test_solution_path = repr(
            str(Path(os.path.realpath(__file__)).parent.parent.joinpath('resources', 'test_solution', '*.py')))
        run_sol_path = repr(str(Path(self.tmp_dir.name).joinpath('run_solution.py')))
        hook_path = repr(str(pkg_resources.resource_filename('album.package.resources', 'install_all.py')))

        datas_string = "\t\t\t datas=[(%s, '.'),(%s, 'subscripts'),(%s, 'solution_files')],\n" % (
            yml_path, run_sol_path, test_solution_path)
        hook_string = "\t\t\t runtime_hooks=[%s],\n" % hook_path

        create_spec_file_no_gui.create(self.tmp_dir.name,
                                       Path(os.path.realpath(__file__)).parent.parent.parent.joinpath('test_package',
                                                                                                      'resources',
                                                                                                      'test_solution',
                                                                                                      'solution.py'))
        created_spec_no_gui = Path(self.tmp_dir.name).joinpath('build_executable.spec')

        counter = 0
        with open(created_spec_no_gui, 'r') as file:
            for line in file:
                if line.startswith("\t\t\t datas="):
                    data_line = line
                    counter += 1
                if line.startswith("\t\t\t runtime_hooks="):
                    hook_line = line
                    counter += 1

        self.assertTrue(os.path.isfile(created_spec_no_gui))
        self.assertEqual(datas_string, data_line)
        self.assertEqual(hook_string, hook_line)
        self.assertEqual(counter, 2)

    def test_run_solution(self):
        base_path = "album = Album.Builder().base_cache_path(%s).build()\n" % repr(
            str(Path.home().joinpath('.album', 'envs', 'album')))
        solution_coords = "album.run(%s, params)\n" % "\'album:import_unittest:0.1.0\'"

        create_subscripts_no_gui.create_run_solution(self.tmp_dir.name, "album:import_unittest:0.1.0")
        created_py_no_gui = Path(self.tmp_dir.name).joinpath('run_solution.py')
        counter = 0
        with open(created_py_no_gui, 'r') as file:
            for line in file:
                if line.startswith("album = "):
                    base_line = line
                    counter += 1
                if line.startswith("album.run("):
                    coords_line = line
                    counter += 1

        self.assertTrue(os.path.isfile(created_py_no_gui))
        self.assertEqual(base_path, base_line)
        self.assertEqual(solution_coords, coords_line)
        self.assertEqual(counter, 2)

    def test_yml(self):
        ver_str = "      - album==%s\n" % core.__version__

        create_subscripts_no_gui.create_yml(self.tmp_dir.name)
        yml_path = Path(self.tmp_dir.name).joinpath('album.yml')
        counter = 0
        with open(yml_path, 'r') as file:
            for line in file:
                if line.startswith("      - album=="):
                    ver_line = line
                    counter += 1

        self.assertTrue(os.path.isfile(yml_path))
        self.assertEqual(ver_str, ver_line)
        self.assertEqual(counter, 1)


if __name__ == '__main__':
    unittest.main()
