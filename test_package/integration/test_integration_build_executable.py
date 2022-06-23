import os
import platform
import subprocess
import unittest
import pexpect
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
            exe_path = Path(self.tmp_dir.name).joinpath('solution', 'solution.exe')
        else:
            exe_path = Path(self.tmp_dir.name).joinpath('solution', 'solution')

        #try:
        cmd = [str(exe_path)]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate(input=b"--run_command amk")


        #finally:
        self.assertTrue(os.path.isfile(exe_path) and os.access(exe_path, os.X_OK),
                        "No executable created or executable not accessible.")
        self.assertEqual(0, p.returncode, "Executable could not be executed correctly.")

    def test_execute_gui(self):
        # build an executable and see if it was successfully build
        build_executable.run(
            self.album_mock,
            Namespace(
                solution=pkg_resources.resource_filename('test_package.resources.test_solution', 'solution.py'),
                output_path=self.tmp_dir.name,
                no_gui=False
            )
        )

        if platform.system() == 'Windows':
            exe_path = Path(self.tmp_dir.name).joinpath('solution', 'solution.exe')
        else:
            exe_path = Path(self.tmp_dir.name).joinpath('solution', 'solution')

        self.assertTrue(os.path.isfile(exe_path) and os.access(exe_path, os.X_OK),
                        "No executable created or executable not accessible.")

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
        with self.assertLogs(get_active_logger(), level='ERROR') as cm:
            build_executable.run(self.album_mock, Namespace(solution=
            Path(os.path.realpath(__file__)).parent.parent.parent.joinpath(
                'test_package',
                'resources',
                'test_solution',
                'murks.py'),
                output_path=Path(self.tmp_dir.name).joinpath('test_output'),
                no_gui=True))

        self.assertEqual('ERROR:root:Solution could not be found! Abort.', cm.output[0],
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
