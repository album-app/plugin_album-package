import os
import platform
import re
import subprocess
import sys
import unittest
from argparse import Namespace
from pathlib import Path

import pkg_resources

from album.package import build_executable
from album.runner.album_logging import get_active_logger
from test_package.test_common import TestCommon


class TestIntegrationBuildExecutable(TestCommon):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_execute_no_gui(self):
        # build an executable and try running it
        build_executable.run(
            self.album_mock,
            Namespace(
                solution=Path(os.path.realpath(__file__)).parent.parent.parent.joinpath(
                    'test_package',
                    'resources',
                    'test_solution'
                ),
                output_path=self.tmp_dir.name,
                no_gui=True
            )
        )

        if platform.system() == 'Windows':
            exe_path = Path(self.tmp_dir.name).joinpath('solution.exe')
        else:
            exe_path = Path(self.tmp_dir.name).joinpath('solution')
        print("VERSION TEST NO GUI : %s !!!!!!!!!!!!!!!!!!!!!!" %sys.version)
        coord_str = 'album.run(\'album:import_unittest:0.1.0\', params)\n'
        conda_str = 'os.environ["ALBUM_CONDA_PATH"] = \'conda\'\n'
        counter = 0
        coord_str_uninstall = 'album.uninstall(\'album:import_unittest:0.1.0\')\n'
        conda_str_uninstall = 'os.environ["ALBUM_CONDA_PATH"] = \'conda\'\n'
        counter_uninstall = 0

        cmd = [str(exe_path)]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        p1 = p.communicate()
        print(p1)
        print("RETURNCODE!!! %s"%p.returncode)

        with open(Path.home().joinpath('.album', 'Solution_shortcuts', 'album_import_unittest_0.1.0', 'run_solution.py'), 'r') as file:
            for line in file:
                if line.startswith("album.run("):
                    coord_line = line
                    counter += 1
                if line.startswith("os.environ["):
                    conda_line = line
                    counter += 1

        with open(Path.home().joinpath('.album', 'Solution_shortcuts', 'album_import_unittest_0.1.0', 'uninstall_solution.py'), 'r') as file:
            for line in file:
                if line.startswith("album.uninstall("):
                    coord_line_uninstall = line
                    counter_uninstall += 1
                if line.startswith("os.environ["):
                    conda_line_uninstall = line
                    counter_uninstall += 1

        self.assertTrue(os.path.isfile(exe_path) and os.access(exe_path, os.X_OK),
                        "No executable created or executable not accessible.")
        self.assertEqual(0, p.returncode, "Executable could not be executed correctly.")
        self.assertEqual(coord_str, coord_line, "The coordinates did not got replaced correctly in the run_solution.py")
        self.assertEqual(conda_str, conda_line, "The path of the conda executable did not got replaced correctly in the run_solution.py")
        self.assertEqual(2, counter, "The many lies got altered in the template the run_solution.py.")
        self.assertEqual(coord_str_uninstall, coord_line_uninstall, "The coordinates did not got replaced correctly in the uninstall_solution.py")
        self.assertEqual(conda_str_uninstall, conda_line_uninstall, "The path of the conda executable did not got replaced correctly in the uninstall_solution.py")
        self.assertEqual(2, counter_uninstall, "The many lies got altered in the uninstall_solution template.")

        if platform.system() == 'Windows':
            self.assertTrue(os.path.isfile(Path.home().joinpath('.album', 'Solution_shortcuts', 'album_icon_windows.ico')))
        elif platform.system() == 'Darwin':
            self.assertTrue(
                os.path.isfile(Path.home().joinpath('.album', 'Solution_shortcuts', 'album_icon_macos.icns')))
        elif platform.system() == 'Linux':
            self.assertTrue(
                os.path.isfile(Path.home().joinpath('.album', 'Solution_shortcuts', 'album_icon_linux.png')))

    def test_execute_gui(self):
        self.maxDiff = None
        # build an executable and see if it was successfully build
        build_executable.run(
            self.album_mock,
            Namespace(
                solution=pkg_resources.resource_filename('test_package.resources.test_solution', 'solution.py'),
                output_path=self.tmp_dir.name,
                no_gui=False
            )
        )
        # create correct output
        if platform.system() == 'Windows':
            exe_path = Path(self.tmp_dir.name).joinpath('solution.exe')
        else:
            exe_path = Path(self.tmp_dir.name).joinpath('solution')
        coord_str = 'album:import_unittest:0.1.0'
        with open(pkg_resources.resource_filename('album.package.resources.templates.gui', 'run_solution_gui_template.py'),'r') as file:
            template_str = file.read()
        template_str = re.sub("<solution>", coord_str, template_str)

        with open(pkg_resources.resource_filename('album.package.resources.templates.gui', 'uninstall_solution_gui_template.py'),'r') as file:
            template_str_uninstall = file.read()
        template_str_uninstall = re.sub("<solution>", coord_str, template_str_uninstall)
        print("VERSION TEST GUI : %s !!!!!!!!!!!!!!!!!!!!!!" % sys.version)
        # call
        cmd = [str(exe_path)]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        p1 = p.communicate()
        print(p1)
        print("RETURNCODE!!! %s"%p.returncode)
        with open(Path.home().joinpath('.album', 'Solution_shortcuts', 'album_import_unittest_0.1.0',
                                       'run_solution_gui.py')) as file:
            created_str = file.read()
        with open(Path.home().joinpath('.album', 'Solution_shortcuts', 'album_import_unittest_0.1.0',
                                       'uninstall_solution_gui.py')) as file:
            created_str_uninstall = file.read()

        print(template_str)
        print("!!!!!!!!!!!")
        print(created_str)


        # assert
        self.assertTrue(os.path.isfile(exe_path) and os.access(exe_path, os.X_OK),
                        "No executable created or executable not accessible.")
        self.assertEqual(0, p.returncode, "Executable could not be executed correctly.")
        self.assertEqual(template_str, created_str, "The coordinates did not got replaced correctly in the run_solution.py")
        self.assertEqual(template_str_uninstall , created_str_uninstall ,
                         "The coordinates did not got replaced correctly in the uninstall _solution.py")
        if platform.system() == 'Windows':
            self.assertTrue(os.path.isfile(Path.home().joinpath('.album', 'Solution_shortcuts', 'album_icon_windows.ico')))
        elif platform.system() == 'Darwin':
            self.assertTrue(
                os.path.isfile(Path.home().joinpath('.album', 'Solution_shortcuts', 'album_icon_macos.icns')))
        elif platform.system() == 'Linux':
            self.assertTrue(
                os.path.isfile(Path.home().joinpath('.album', 'Solution_shortcuts', 'album_icon_linux.png')))

    def test_output_path(self):
        # test if an output path that didn't exist prior to the test was created
        build_executable.run(self.album_mock, Namespace(
            solution=pkg_resources.resource_filename('test_package.resources.test_solution', 'solution.py'),
            output_path=Path(self.tmp_dir.name).joinpath('test_output'),
            no_gui=True))

        self.assertTrue(os.path.isdir(Path(self.tmp_dir.name).joinpath('test_output')),
                        "Output directory was not created.")

    def test_no_solution(self):
        # test if the plugin aborts if the solution is missing
        self.album_mock.resolve.return_value = "BOOLSHIT"
        with self.assertLogs(get_active_logger(), level='ERROR') as cm:
            build_executable.run(self.album_mock, Namespace(solution=
            Path(os.path.realpath(__file__)).parent.parent.parent.joinpath(
                'test_package',
                'resources',
                'test_solution',
                'murks.py'),
                output_path=Path(self.tmp_dir.name).joinpath('test_output'),
                no_gui=True))

        error_str = "ERROR:root:album command failed: Cannot find solution %s! " \
                    "Try <doi>:<prefix>/<suffix> or <prefix>/<suffix> or <group>:<name>:<version> or " \
                    "<catalog>:<group>:<name>:<version> or point to a valid file! Aborting..." % Path(
            os.path.realpath(__file__)).parent.parent.parent.joinpath('test_package', 'resources', 'test_solution',
                                                                      'murks.py')

        self.assertEqual(error_str, cm.output[0],
                         "Missing solution was not caught.")

    def test_clean_up_no_gui(self):
        # test if the cleanup was done
        build_executable.run(self.album_mock, Namespace(
            solution=pkg_resources.resource_filename('test_package.resources.test_solution', 'solution.py'),
            output_path=self.tmp_dir.name,
            no_gui=True))

        self.assertFalse(os.path.isfile(Path(self.tmp_dir.name).joinpath('run_solution.py')),
                         "run_solution.py was not deleted.")
        self.assertFalse(os.path.isfile(Path(self.tmp_dir.name).joinpath('call_solution.py')),
                         "call_solution.py was not deleted.")
        self.assertFalse(os.path.isfile(Path(self.tmp_dir.name).joinpath('build_executable.spec')),
                         "build_executable.spec was not deleted.")
        self.assertFalse(os.path.isdir(Path(self.tmp_dir.name).joinpath('build')),
                         "PyInstallers build directory was not deleted.")

    def test_clean_up_gui(self):
        # test if the cleanup was done
        build_executable.run(self.album_mock, Namespace(
            solution=pkg_resources.resource_filename('test_package.resources.test_solution', 'solution.py'),
            output_path=self.tmp_dir.name,
            no_gui=False))

        self.assertFalse(os.path.isdir(Path(self.tmp_dir.name).joinpath('build')),
                         "PyInstallers build directory was not deleted.")
        self.assertFalse(os.path.isfile(Path(self.tmp_dir.name).joinpath('call_solution_gui.py')),
                         "call_solution_gui.py was not deleted.")
        self.assertFalse(os.path.isfile(Path(self.tmp_dir.name).joinpath('build_executable_gui.spec')),
                         "build_executable_gui.spec was not deleted.")


if __name__ == '__main__':
    unittest.main()
