import inspect
import os
import platform
import sys
import unittest.mock
from pathlib import Path

import pkg_resources

from album import core
from album.argument_parsing import create_parser
from album.package import create_specfile, create_subscripts
from album.package.argument_parsing import album_package
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
        self.assertEqual("An_example_path", args[0].output_path)
        self.assertEqual(inspect.getsource(album_package), inspect.getsource(args[0].func))

        sys.argv = ["", "package", "1234", "An_example_path"]
        args = parser.parse_known_args()
        self.assertEqual("1234", args[0].solution)
        self.assertEqual("An_example_path", args[0].output_path)
        self.assertEqual(inspect.getsource(album_package), inspect.getsource(args[0].func))

    def test_entrypoint(self):
        create_subscripts.create_execution_entrypoint(self.tmp_dir.name)
        self.assertTrue(Path(self.tmp_dir.name).joinpath('execution_entrypoint.py').is_file())

    def test_call_solution_gui(self):
        # test if the call_solution_gui_template was successfully created
        test_coords = '    coordinates = \'album:import_unittest:0.1.0\'\n'
        create_subscripts.create_call_solution(self.tmp_dir.name, 'album:import_unittest:0.1.0')
        created_call_solution = Path(self.tmp_dir.name).joinpath('call_solution.py')

        counter = 0
        with open(created_call_solution, 'r') as file:
            for line in file:
                if line.startswith("    coordinates ="):
                    coord_line = line
                    counter += 1

        self.assertTrue(Path(self.tmp_dir.name).joinpath('call_solution.py').is_file(),
                        "There was no call_solution.py subscript created!")
        self.assertEqual(test_coords, coord_line,
                        'There was an error inserting the solution coordinates into the call_solution.py!')
        self.assertEqual(2, counter, 'The coordinates got inserted more than one time!')

    def test_spec_file_single(self):
        yml_path = repr(str(Path(self.tmp_dir.name).joinpath('album.yml')))
        test_solution_path = repr(
            str(Path(os.path.realpath(__file__)).parent.parent.joinpath('resources', 'test_solution', 'solution.py')))
        hook_path = repr(str(pkg_resources.resource_filename('album.package.resources.installer', 'install_all.py')))
        call_sol_path = repr(str(Path(self.tmp_dir.name).joinpath('call_solution.py')))
        run_sol_gui_path = repr(
            str(pkg_resources.resource_filename('album.package.resources.templates',
                                                'run_solution_gui.template')))
        uninstall_sol_gui_path = repr(
            str(pkg_resources.resource_filename('album.package.resources.templates',
                                                'uninstall_solution_gui.template')))
        run_sol_path = repr(
            str(pkg_resources.resource_filename('album.package.resources.templates',
                                                'run_solution.template')))
        uninstall_sol_path = repr(
            str(pkg_resources.resource_filename('album.package.resources.templates',
                                                'uninstall_solution.template')))

        if platform.system() == 'Windows':
            icon_path = repr(
                str(pkg_resources.resource_filename('album.package.resources.icons', 'album_icon_windows.ico')))
            installer_path = repr(str(pkg_resources.resource_filename('album.package.resources.installer',
                                                                      'Miniconda_installer_windows.exe')))
        elif platform.system() == 'Darwin':
            icon_path = repr(
                str(pkg_resources.resource_filename('album.package.resources.icons', 'album_icon_macos.icns')))
            installer_path = repr(str(pkg_resources.resource_filename('album.package.resources.installer',
                                                                      'Miniconda_installer_macos.sh')))
        elif platform.system() == 'Linux':
            icon_path = repr(
                str(pkg_resources.resource_filename('album.package.resources.icons', 'album_icon_linux.png')))
            installer_path = repr(str(pkg_resources.resource_filename('album.package.resources.installer',
                                                                      'Miniconda_installer_linux.sh')))
        else:
            print("Your OS is currently not supported")
            raise NotImplementedError

        datas_string = "\t\t\t datas=[(%s, '.'),(%s, 'solution_files'),(%s, '.'),(%s, '.'),(%s, '.'),(%s, '.'),(%s, '.'),(%s, '.'),(%s, '.')],\n" % (yml_path, test_solution_path, run_sol_path, uninstall_sol_path, icon_path, run_sol_gui_path, uninstall_sol_gui_path, call_sol_path, installer_path)
        hook_string = "\t\t\t runtime_hooks=[%s],\n" % hook_path

        create_specfile.create(self.tmp_dir.name,
                                    Path(os.path.realpath(__file__)).parent.parent.parent.joinpath('test_package',
                                                                                                   'resources',
                                                                                                   'test_solution',
                                                                                                   'solution.py'))
        created_spec_gui = Path(self.tmp_dir.name).joinpath('build_executable.spec')

        counter = 0
        with open(created_spec_gui, 'r') as file:
            for line in file:
                if line.startswith("\t\t\t datas="):
                    data_line = line
                    counter += 1
                if line.startswith("\t\t\t runtime_hooks="):
                    hook_line = line
                    counter += 1

        self.assertTrue(Path(created_spec_gui).is_file(), "There was no spec file created!")
        self.assertEqual(datas_string, data_line,
                         "There was an error creating the string for additional data in the spec file.")
        self.assertEqual(hook_string, hook_line,
                         "There was an error creating the string for the install script in the spec file.")
        self.assertEqual(2, counter, "There were to many lines replaced! Error in the spec file creation")

    def test_spec_file_dir(self):
        yml_path = repr(str(Path(self.tmp_dir.name).joinpath('album.yml')))
        test_solution_path = repr(
            str(Path(os.path.realpath(__file__)).parent.parent.joinpath('resources', 'test_solution', '*')))
        hook_path = repr(str(pkg_resources.resource_filename('album.package.resources.installer', 'install_all.py')))
        call_sol_path = repr(str(Path(self.tmp_dir.name).joinpath('call_solution.py')))
        run_sol_gui_path = repr(
            str(pkg_resources.resource_filename('album.package.resources.templates',
                                                'run_solution_gui.template')))
        uninstall_sol_gui_path = repr(
            str(pkg_resources.resource_filename('album.package.resources.templates',
                                                'uninstall_solution_gui.template')))
        run_sol_path = repr(
            str(pkg_resources.resource_filename('album.package.resources.templates',
                                                'run_solution.template')))
        uninstall_sol_path = repr(
            str(pkg_resources.resource_filename('album.package.resources.templates',
                                                'uninstall_solution.template')))

        if platform.system() == 'Windows':
            icon_path = repr(
                str(pkg_resources.resource_filename('album.package.resources.icons', 'album_icon_windows.ico')))
            installer_path = repr(str(pkg_resources.resource_filename('album.package.resources.installer',
                                                                      'Miniconda_installer_windows.exe')))
        elif platform.system() == 'Darwin':
            icon_path = repr(
                str(pkg_resources.resource_filename('album.package.resources.icons', 'album_icon_macos.icns')))
            installer_path = repr(str(pkg_resources.resource_filename('album.package.resources.installer',
                                                                      'Miniconda_installer_macos.sh')))
        elif platform.system() == 'Linux':
            icon_path = repr(
                str(pkg_resources.resource_filename('album.package.resources.icons', 'album_icon_linux.png')))
            installer_path = repr(str(pkg_resources.resource_filename('album.package.resources.installer',
                                                                      'Miniconda_installer_linux.sh')))
        else:
            print("Your OS is currently not supported")
            raise NotImplementedError

        datas_string = "\t\t\t datas=[(%s, '.'),(%s, 'solution_files'),(%s, '.'),(%s, '.'),(%s, '.'),(%s, '.'),(%s, '.'),(%s, '.'),(%s, '.')],\n" % (
        yml_path, test_solution_path, run_sol_path, uninstall_sol_path, icon_path, run_sol_gui_path,
        uninstall_sol_gui_path, call_sol_path, installer_path)
        hook_string = "\t\t\t runtime_hooks=[%s],\n" % hook_path

        create_specfile.create(self.tmp_dir.name,
                               Path(os.path.realpath(__file__)).parent.parent.parent.joinpath('test_package',
                                                                                              'resources',
                                                                                              'test_solution'))
        created_spec_gui = Path(self.tmp_dir.name).joinpath('build_executable.spec')

        counter = 0
        with open(created_spec_gui, 'r') as file:
            for line in file:
                if line.startswith("\t\t\t datas="):
                    data_line = line
                    counter += 1
                if line.startswith("\t\t\t runtime_hooks="):
                    hook_line = line
                    counter += 1

        self.assertTrue(Path(created_spec_gui).is_file(), "There was no spec file created!")
        self.assertEqual(datas_string, data_line,
                         "There was an error creating the string for additional data in the spec file.")
        self.assertEqual(hook_string, hook_line,
                         "There was an error creating the string for the install script in the spec file.")
        self.assertEqual(counter, 2, "There were to many lines replaced! Error in the spec file creation")

    def test_yml(self):
        # test if the yml file was correctly created
        ver_str = "      - album==%s\n" % core.__version__

        create_subscripts.create_yml(self.tmp_dir.name)
        yml_path = Path(self.tmp_dir.name).joinpath('album.yml')
        counter = 0
        with open(yml_path, 'r') as file:
            for line in file:
                if line.startswith("      - album=="):
                    ver_line = line
                    counter += 1

        self.assertTrue(Path(yml_path).is_file(), "There was no album.yml file created!")
        self.assertEqual(ver_str, ver_line, "An error occured when inserting the current album version!")
        self.assertEqual(counter, 1, "There were to many lines replaced! Error in the album.yml creation")


if __name__ == '__main__':
    unittest.main()
