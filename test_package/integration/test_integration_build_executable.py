import os
import platform
import unittest
from argparse import Namespace
from pathlib import Path

from album.package import build_executable
from album.runner.album_logging import get_active_logger
from test_package.test_common import TestCommon


class TestIntegrationBuildExecutable(TestCommon):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_execute_no_gui(self):
        # TODO: Check if exe is executed the right way

        build_executable.run(
            self.album_mock,
            Namespace(
                solution=Path(os.path.realpath(__file__)).parent.parent.parent.joinpath(
                    'test_package',
                    'resources',
                    'test_solution',
                    'solution.py'
                ),
                output_path=self.tmp_dir.name,
                no_gui=True
            )
        )

        if platform.system() == 'Windows':
            exe_path = Path(self.tmp_dir.name).joinpath('solution', 'solution.exe')
        else:
            exe_path = Path(self.tmp_dir.name).joinpath('solution', 'solution')

        self.assertTrue(os.path.isfile(exe_path) and os.access(exe_path, os.X_OK))

    def test_execute_gui(self):
        build_executable.run(
            self.album_mock,
            Namespace(
                solution=Path(os.path.realpath(__file__)).parent.parent.parent.joinpath(
                    'test_package',
                    'resources',
                    'test_solution',
                    'solution.py'
                ),
                output_path=self.tmp_dir.name,
                no_gui=False
            )
        )

        if platform.system() == 'Windows':
            exe_path = Path(self.tmp_dir.name).joinpath('solution', 'solution.exe')
        else:
            exe_path = Path(self.tmp_dir.name).joinpath('solution', 'solution')

        self.assertTrue(os.path.isfile(exe_path) and os.access(exe_path, os.X_OK))

    def test_output_path(self):
        build_executable.run(self.album_mock, Namespace(solution=
        Path(os.path.realpath(__file__)).parent.parent.parent.joinpath(
            'test_package',
            'resources',
            'test_solution',
            'solution.py'),
            output_path=Path(self.tmp_dir.name).joinpath('test_output'),
            no_gui=True))

        self.assertTrue(os.path.isdir(Path(self.tmp_dir.name).joinpath('test_output')))

    def test_no_solution(self):
        with self.assertLogs(get_active_logger(), level='ERROR') as cm:
            build_executable.run(self.album_mock, Namespace(solution=
            Path(os.path.realpath(__file__)).parent.parent.parent.joinpath(
                'test_package',
                'resources',
                'test_solution',
                'murks.py'),
                output_path=Path(self.tmp_dir.name).joinpath('test_output'),
                no_gui=True))

        self.assertEqual('ERROR:root:Solution could not be found! Abort.', cm.output[0])

    def test_clean_up_no_gui(self):
        build_executable.run(self.album_mock, Namespace(solution=
        Path(os.path.realpath(__file__)).parent.parent.parent.joinpath(
            'src',
            'resources',
            'test_solution',
            'solution.py'),
            output_path=self.tmp_dir.name,
            no_gui=True))

        self.assertFalse(os.path.isfile(Path(self.tmp_dir.name).joinpath('run_solution_template.py')))
        self.assertFalse(os.path.isfile(Path(self.tmp_dir.name).joinpath('call_solution.py')))
        self.assertFalse(os.path.isfile(Path(self.tmp_dir.name).joinpath('install_hook.py')))
        self.assertFalse(os.path.isfile(Path(self.tmp_dir.name).joinpath('build_executable.spec')))
        self.assertFalse(os.path.isdir(Path(self.tmp_dir.name).joinpath('build')))

    def test_clean_up_gui(self):
        build_executable.run(self.album_mock, Namespace(solution=
        Path(os.path.realpath(__file__)).parent.parent.parent.joinpath(
            'test_package',
            'resources',
            'test_solution',
            'solution.py'),
            output_path=self.tmp_dir.name,
            no_gui=False))

        self.assertFalse(os.path.isdir(Path(self.tmp_dir.name).joinpath('build')))
        self.assertFalse(os.path.isfile(Path(self.tmp_dir.name).joinpath('call_solution_gui.py')))
        self.assertFalse(os.path.isfile(Path(self.tmp_dir.name).joinpath('install_hook.py')))
        self.assertFalse(os.path.isfile(Path(self.tmp_dir.name).joinpath('build_executable_gui.spec')))

if __name__ == '__main__':
    unittest.main()
