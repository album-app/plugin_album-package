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
        # test the argument pasring
        parser = create_parser()
        sys.argv = ["", "package", "1234", "An_example_path"]
        args = parser.parse_known_args()
        self.assertEqual("1234", args[0].solution)
        self.assertEqual(False, args[0].no_gui)
        self.assertEqual("An_example_path", args[0].output_path)
        self.assertEqual(inspect.getsource(build_executable.run), inspect.getsource(args[0].func))

        sys.argv = ["", "package", "1234", "An_example_path", "--no_gui"]
        args = parser.parse_known_args()
        self.assertEqual("1234", args[0].solution)
        self.assertEqual(True, args[0].no_gui)
        self.assertEqual("An_example_path", args[0].output_path)
        self.assertEqual(inspect.getsource(build_executable.run), inspect.getsource(args[0].func))

    def test_call_solution_gui(self):
        # test if the call_solution_gui_template was successfully created
        test_coords = '    coordinates = \'album:import_unittest:0.1.0\'\n'
        create_subscripts_gui.create_call_solution(self.tmp_dir.name, 'album:import_unittest:0.1.0')
        created_call_solution = Path(self.tmp_dir.name).joinpath('call_solution_gui.py')

        counter = 0
        with open(created_call_solution, 'r') as file:
            for line in file:
                if line.startswith("    coordinates ="):
                    coord_line = line
                    counter += 1

        self.assertTrue(os.path.isfile(Path(self.tmp_dir.name).joinpath('call_solution_gui.py')),
                        "There was no call_solution_gui.py subscript created!")
        self.assertEqual(test_coords, coord_line,
                        'There was an error inserting the solution coordinates into the call_solution_gui.py!')
        self.assertEqual(1, counter, 'The coordinates got inserted more than one time!')


    def test_call_solution_no_gui(self):
        # test if the call_solution_template was successfully created
        test_coords = '    coordinates = \'album:import_unittest:0.1.0\'\n'
        create_subscripts_no_gui.create_call_solution(self.tmp_dir.name, 'album:import_unittest:0.1.0')
        created_call_solution = Path(self.tmp_dir.name).joinpath('call_solution.py')

        counter = 0
        with open(created_call_solution, 'r') as file:
            for line in file:
                if line.startswith("    coordinates ="):
                    coord_line = line
                    counter += 1

        self.assertTrue(os.path.isfile(Path(self.tmp_dir.name).joinpath('call_solution.py')),
                        "There was no call_solution.py subscript created!")
        self.assertEqual(test_coords, coord_line,
                        'There was an error inserting the solution coordinates into the call_solution.py!')
        self.assertEqual(1, counter, 'The coordinates got inserted more than one time!')

    def test_spec_file_gui_single(self):
        # test if the specfile was generated correctly for the single solution gui mode
        yml_path = repr(str(Path(self.tmp_dir.name).joinpath('album.yml')))
        test_solution_path = repr(
            str(Path(os.path.realpath(__file__)).parent.parent.joinpath('resources', 'test_solution', 'solution.py')))
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

        self.assertTrue(os.path.isfile(created_spec_gui), "There was no spec file created!")
        self.assertEqual(datas_string, data_line,
                         "There was an error creating the string for additional data in the spec file.")
        self.assertEqual(hook_string, hook_line,
                         "There was an error creating the string for the install script in the spec file.")
        self.assertEqual(counter, 2, "There were to many lines replaced! Error in the spec file creation")

    def test_spec_file_no_gui_single(self):
        # test if the specfile was generated correctly for the single solution no gui mode
        yml_path = repr(str(Path(self.tmp_dir.name).joinpath('album.yml')))
        test_solution_path = repr(
            str(Path(os.path.realpath(__file__)).parent.parent.joinpath('resources', 'test_solution', 'solution.py')))
        hook_path = repr(str(pkg_resources.resource_filename('album.package.resources', 'install_all.py')))

        datas_string = "\t\t\t datas=[(%s, '.'),(%s, 'solution_files')],\n" % (
            yml_path, test_solution_path)
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

        self.assertTrue(os.path.isfile(created_spec_no_gui), "There was no spec file created!")
        self.assertEqual(datas_string, data_line,
                         "There was an error creating the string for additional data in the spec file.")
        self.assertEqual(hook_string, hook_line,
                         "There was an error creating the string for the install script in the spec file.")
        self.assertEqual(counter, 2, "There were to many lines replaced! Error in the spec file creation")

    def test_spec_file_gui_dir(self):
        # test if the specfile was generated correctly for the solution directory gui mode
        yml_path = repr(str(Path(self.tmp_dir.name).joinpath('album.yml')))
        test_solution_path = repr(
            str(Path(os.path.realpath(__file__)).parent.parent.joinpath('resources', 'test_solution', '*')))
        hook_path = repr(str(pkg_resources.resource_filename('album.package.resources', 'install_all.py')))

        datas_string = "\t\t\t datas=[(%s, '.'),(%s, 'solution_files')],\n" % (yml_path, test_solution_path)
        hook_string = "\t\t\t runtime_hooks=[%s],\n" % hook_path

        create_spec_file_gui.create(self.tmp_dir.name,
                                    Path(os.path.realpath(__file__)).parent.parent.parent.joinpath('test_package',
                                                                                                   'resources',
                                                                                                   'test_solution'))
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
        self.maxDiff = None
        self.assertTrue(os.path.isfile(created_spec_gui), "There was no spec file created!")
        self.assertEqual(datas_string, data_line,
                         "There was an error creating the string for additional data in the spec file.")
        self.assertEqual(hook_string, hook_line,
                         "There was an error creating the string for the install script in the spec file.")
        self.assertEqual(counter, 2, "There were to many lines replaced! Error in the spec file creation")

    def test_spec_file_no_gui_dir(self):
        # test if the specfile was generated correctly for the solution directory no gui mode
        yml_path = repr(str(Path(self.tmp_dir.name).joinpath('album.yml')))
        test_solution_path = repr(
            str(Path(os.path.realpath(__file__)).parent.parent.joinpath('resources', 'test_solution', '*')))
        hook_path = repr(str(pkg_resources.resource_filename('album.package.resources', 'install_all.py')))

        datas_string = "\t\t\t datas=[(%s, '.'),(%s, 'solution_files')],\n" % (
            yml_path, test_solution_path)
        hook_string = "\t\t\t runtime_hooks=[%s],\n" % hook_path

        create_spec_file_no_gui.create(self.tmp_dir.name,
                                       Path(os.path.realpath(__file__)).parent.parent.parent.joinpath('test_package',
                                                                                                      'resources',
                                                                                                      'test_solution'))
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

        self.maxDiff = None
        self.assertTrue(os.path.isfile(created_spec_no_gui), "There was no spec file created!")
        self.assertEqual(datas_string, data_line,
                         "There was an error creating the string for additional data in the spec file.")
        self.assertEqual(hook_string, hook_line,
                         "There was an error creating the string for the install script in the spec file.")
        self.assertEqual(counter, 2, "There were to many lines replaced! Error in the spec file creation")

    def test_yml(self):
        # test if the yml file was correctly created
        ver_str = "      - album==%s\n" % core.__version__

        create_subscripts_no_gui.create_yml(self.tmp_dir.name)
        yml_path = Path(self.tmp_dir.name).joinpath('album.yml')
        counter = 0
        with open(yml_path, 'r') as file:
            for line in file:
                if line.startswith("      - album=="):
                    ver_line = line
                    counter += 1

        self.assertTrue(os.path.isfile(yml_path), "There was no album.yml file created!")
        self.assertEqual(ver_str, ver_line, "An error occured when inserting the current album version!")
        self.assertEqual(counter, 1, "There were to many lines replaced! Error in the album.yml creation")


if __name__ == '__main__':
    unittest.main()
