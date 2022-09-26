import os
import platform
import subprocess
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

import pkg_resources

from album.package import build_executable
from album.runner.album_logging import get_active_logger
from test_package.test_common import TestCommon


class TestIntegrationBuildExecutable(TestCommon):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    # @unittest.skipIf(sys.platform == 'win32' or sys.platform == 'cygwin',
    #                 "The windows runner doens't work with pywin32")
    @unittest.skip
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
                output_path=self.tmp_dir.name
            )
        )

        if platform.system() == 'Windows':
            exe_path = Path(self.tmp_dir.name).joinpath('solution.exe')
        else:
            exe_path = Path(self.tmp_dir.name).joinpath('solution')

        coord_str = 'coords = \'album:import_unittest:0.1.0\'\n'
        conda_str = 'os.environ["ALBUM_CONDA_PATH"] = \'conda\'\n'
        counter = 0
        coord_str_uninstall = 'album.uninstall(\'album:import_unittest:0.1.0\')\n'
        conda_str_uninstall = 'os.environ["ALBUM_CONDA_PATH"] = \'conda\'\n'
        counter_uninstall = 0

        cmd = [str(exe_path)]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        p1 = p.communicate(b'n')

        if platform.system() == 'Darwin':
            with open(Path.home().joinpath('.album', 'Solution_shortcuts', 'album_import_unittest_0_1_0',
                                           'run_solution.py'), 'r') as file:
                for line in file:
                    if "coords =" in line:
                        coord_line = line
                        counter += 1
                    if "os.environ[" in line:
                        conda_line = line
                        counter += 1

            with open(Path.home().joinpath('.album', 'Solution_shortcuts', 'album_import_unittest_0_1_0',
                                           'uninstall_solution.py'), 'r') as file:
                for line in file:
                    if "album.uninstall(" in line:
                        coord_line_uninstall = line
                        counter_uninstall += 1
                    if "os.environ[" in line:
                        conda_line_uninstall = line
                        counter_uninstall += 1
        else:
            with open(Path.home().joinpath('.album', 'Solution_shortcuts', 'album_import_unittest_0.1.0',
                                           'run_solution.py'), 'r') as file:
                for line in file:
                    if "coords =" in line:
                        coord_line = line
                        counter += 1
                    if "os.environ[" in line:
                        conda_line = line
                        counter += 1

            with open(Path.home().joinpath('.album', 'Solution_shortcuts', 'album_import_unittest_0.1.0',
                                           'uninstall_solution.py'), 'r') as file:
                for line in file:
                    if "album.uninstall(" in line:
                        coord_line_uninstall = line
                        counter_uninstall += 1
                    if "os.environ[" in line:
                        conda_line_uninstall = line
                        counter_uninstall += 1

        self.assertTrue(Path(exe_path).is_file() and os.access(exe_path, os.X_OK),
                        "No executable created or executable not accessible.")
        self.assertEqual(0, p.returncode, "Executable could not be executed correctly.")
        self.assertEqual(coord_str, coord_line, "The coordinates did not got replaced correctly in the run_solution.py")
        self.assertEqual(conda_str, conda_line,
                         "The path of the conda executable did not got replaced correctly in the run_solution.py")
        self.assertEqual(2, counter, "The many lies got altered in the template the run_solution.py.")
        self.assertEqual(coord_str_uninstall, coord_line_uninstall,
                         "The coordinates did not got replaced correctly in the uninstall_solution.py")
        self.assertEqual(conda_str_uninstall, conda_line_uninstall,
                         "The path of the conda executable did not got replaced correctly in the uninstall_solution.py")
        self.assertEqual(2, counter_uninstall, "The many lines got altered in the uninstall_solution template.")

        if platform.system() == 'Windows':
            self.assertTrue(Path.home().joinpath('.album', 'Solution_shortcuts', 'album_icon_windows.ico').is_file())
        elif platform.system() == 'Darwin':
            self.assertTrue(
                Path.home().joinpath('.album', 'Solution_shortcuts', 'album_icon_macos.icns').is_file())
        elif platform.system() == 'Linux':
            self.assertTrue(
                Path.home().joinpath('.album', 'Solution_shortcuts', 'album_icon_linux.png').is_file())

    # @unittest.skipIf(sys.platform == 'win32' or sys.platform == 'cygwin',
    #                 "The windows runner doens't work with pywin32")
    @unittest.skip
    def test_execute_gui(self):
        self.maxDiff = None
        # build an executable and see if it was successfully build
        build_executable.run(
            self.album_mock,
            Namespace(
                solution=pkg_resources.resource_filename('test_package.resources.test_solution', 'solution.py'),
                output_path=self.tmp_dir.name
            )
        )
        # create correct output
        if platform.system() == 'Windows':
            exe_path = Path(self.tmp_dir.name).joinpath('solution.exe')
        else:
            exe_path = Path(self.tmp_dir.name).joinpath('solution')
        coord_str = '    run_input = \'album:import_unittest:0.1.0\'\n'
        counter = 0
        counter_uninstall = 0

        # call
        cmd = [str(exe_path)]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        p1 = p.communicate(b'y')
        print(p1[0].decode())

        if platform.system() == 'Darwin':
            with open(Path.home().joinpath('.album', 'Solution_shortcuts', 'album_import_unittest_0_1_0',
                                           'run_solution_gui.py'), 'r') as file:
                for line in file:
                    if "run_input =" in line:
                        coord_line = line
                        counter += 1

            with open(Path.home().joinpath('.album', 'Solution_shortcuts', 'album_import_unittest_0_1_0',
                                           'uninstall_solution_gui.py'), 'r') as file:
                for line in file:
                    if "run_input =" in line:
                        coord_line_uninstall = line
                        counter_uninstall += 1

        else:
            with open(Path.home().joinpath('.album', 'Solution_shortcuts', 'album_import_unittest_0.1.0',
                                           'run_solution_gui.py'), 'r') as file:
                for line in file:
                    if "run_input =" in line:
                        coord_line = line
                        counter += 1

            with open(Path.home().joinpath('.album', 'Solution_shortcuts', 'album_import_unittest_0.1.0',
                                           'uninstall_solution_gui.py'), 'r') as file:
                for line in file:
                    if "run_input =" in line:
                        coord_line_uninstall = line
                        counter_uninstall += 1

        # assert
        self.assertTrue(Path(exe_path).is_file() and os.access(exe_path, os.X_OK),
                        "No executable created or executable not accessible.")
        self.assertEqual(0, p.returncode, "Executable could not be executed correctly.")
        self.assertEqual(coord_str, coord_line, "The coordinates did not got replaced correctly in the run_solution.py")
        self.assertEqual(coord_str, coord_line_uninstall,
                         "The coordinates did not got replaced correctly in the uninstall _solution.py")
        self.assertEqual(1, counter, "The many lies got altered in the template the run_solution.py.")
        self.assertEqual(1, counter_uninstall, "The many lies got altered in the template the uninstall_solution.py.")
        if platform.system() == 'Windows':
            self.assertTrue(Path.home().joinpath('.album', 'Solution_shortcuts', 'album_icon_windows.ico').is_file())
        elif platform.system() == 'Darwin':
            self.assertTrue(
                Path.home().joinpath('.album', 'Solution_shortcuts', 'album_icon_macos.icns').is_file())
        elif platform.system() == 'Linux':
            self.assertTrue(
                Path.home().joinpath('.album', 'Solution_shortcuts', 'album_icon_linux.png').is_file())

    def test_output_path(self):
        # test if an output path that didn't exist prior to the test was created
        build_executable.run(self.album_mock, Namespace(
            solution=pkg_resources.resource_filename('test_package.resources.test_solution', 'solution.py'),
            output_path=Path(self.tmp_dir.name).joinpath('test_output')))

        self.assertTrue(Path(self.tmp_dir.name).joinpath('test_output').is_dir(),
                        "Output directory was not created.")

    @unittest.skip
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

    def test_clean_up(self):
        try:
            # FIXME: Exceptions that occur here are not caught and the test succeeds anyway
            build_executable.run(self.album_mock, Namespace(
                solution=pkg_resources.resource_filename('test_package.resources.test_solution', 'solution.py'),
                output_path=self.tmp_dir.name))
        finally:
            self.assertFalse(Path(self.tmp_dir.name).joinpath('build').is_dir(),
                             "PyInstallers build directory was not deleted.")
            self.assertFalse(
                Path(self.tmp_dir.name).joinpath('album_album_import_unittest_0_1_0_installer.spec').is_file(),
                "build_executable.spec was not deleted.")
            self.assertFalse(Path(self.tmp_dir.name).joinpath('solution_info.txt').is_file(),
                             "solution_info.txt was not deleted.")

    #@patch("pathlib.Path.home")
    #def test_build_album_installer(self, mock_home_call):
    #    # prepare
    #    mock_home_call.return_value = self.tmp_dir
    #    print(Path.home())
    #    cmd = subprocess.run(['python', '-c', 'from pathlib import Path\nprint(Path.home())'])


if __name__ == '__main__':
    unittest.main()
