import os
import platform
import unittest
from argparse import Namespace
from pathlib import Path

from album.executable import build_executable
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
        check = os.path.isfile(exe_path) and os.access(exe_path, os.X_OK)

        self.assertTrue(check)

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
        check = os.path.isfile(exe_path) and os.access(exe_path, os.X_OK)

        self.assertTrue(check)

    def test_output_path(self):
        build_executable.run(self.album_mock, Namespace(solution=
        Path(os.path.realpath(__file__)).parent.parent.parent.joinpath(
            'test_package',
            'resources',
            'test_solution',
            'solution.py'),
            output_path=Path(self.tmp_dir.name).joinpath('test_output'),
            no_gui=True))

        check = os.path.isdir(Path(self.tmp_dir.name).joinpath('test_output'))

        self.assertTrue(check)

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
        check_1 = os.path.isfile(Path(self.tmp_dir.name).joinpath('run_solution.py'))
        check_2 = os.path.isfile(Path(self.tmp_dir.name).joinpath('execute_solution.py'))
        check_3 = os.path.isfile(Path(self.tmp_dir.name).joinpath('install_hook.py'))
        check_4 = os.path.isfile(Path(self.tmp_dir.name).joinpath('build_executable.spec'))
        check_5 = os.path.isdir(Path(self.tmp_dir.name).joinpath('build'))

        self.assertFalse(check_1)
        self.assertFalse(check_2)
        self.assertFalse(check_3)
        self.assertFalse(check_4)
        self.assertFalse(check_5)

    def test_clean_up_gui(self):
        build_executable.run(self.album_mock, Namespace(solution=
        Path(os.path.realpath(__file__)).parent.parent.parent.joinpath(
            'test_package',
            'resources',
            'test_solution',
            'solution.py'),
            output_path=self.tmp_dir.name,
            no_gui=False))

        check_1 = os.path.isdir(Path(self.tmp_dir.name).joinpath('build'))
        check_2 = os.path.isfile(Path(self.tmp_dir.name).joinpath('execute_solution_gui.py'))
        check_3 = os.path.isfile(Path(self.tmp_dir.name).joinpath('install_hook.py'))
        check_4 = os.path.isfile(Path(self.tmp_dir.name).joinpath('build_executable_gui.spec'))

        self.assertFalse(check_1)
        self.assertFalse(check_2)
        self.assertFalse(check_3)
        self.assertFalse(check_4)

if __name__ == '__main__':
    unittest.main()
