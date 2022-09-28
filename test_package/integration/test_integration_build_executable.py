import os
import platform
import subprocess
import time
import unittest
from argparse import Namespace
from pathlib import Path

import pkg_resources

from album.package import build_executable
from test_package.test_common import TestCommon


class TestIntegrationBuildExecutable(TestCommon):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_output_path(self):
        # test if an output path that didn't exist prior to the test was created
        build_executable.run(self.album_mock, Namespace(
            solution=pkg_resources.resource_filename('test_package.resources.test_solution', 'solution.py'),
            output_path=Path(self.tmp_dir.name).joinpath('test_output')))

        self.assertTrue(Path(self.tmp_dir.name).joinpath('test_output').is_dir(),
                        "Output directory was not created.")

    def test_clean_up(self):
        try:
            # FIXME: Exceptions that occur here are not caught and the test succeeds anyway
            build_executable.run(self.album_mock, Namespace(
                solution=pkg_resources.resource_filename('test_package.resources.test_solution', 'solution.py'),
                output_path=self.tmp_dir.name))
        except Exception as e:
            raise RuntimeError("Error in executable building") from e
        finally:
            self.assertFalse(Path(self.tmp_dir.name).joinpath('build').is_dir(),
                             "PyInstallers build directory was not deleted.")
            self.assertFalse(
                Path(self.tmp_dir.name).joinpath('album_album_import_unittest_0_1_0_installer.spec').is_file(),
                "build_executable.spec was not deleted.")
            self.assertFalse(Path(self.tmp_dir.name).joinpath('solution_info.txt').is_file(),
                             "solution_info.txt was not deleted.")

    def test_build_album_installer(self):
        try:
            # FIXME: Exceptions that occur here are not caught and the test succeeds anyway
            build_executable.run(self.album_mock, Namespace(solution=None, output_path=self.tmp_dir.name))
        except Exception as e:
            raise RuntimeError("Error in executable building") from e
        finally:
            if platform.system() == 'Windows':
                self.assertTrue(Path(self.tmp_dir.name).joinpath("album_installer.exe").is_file())
            else:
                self.assertTrue(Path(self.tmp_dir.name).joinpath("album_installer").is_file())

    def test_build_solution_installer(self):
        try:
            # FIXME: Exceptions that occur here are not caught and the test succeeds anyway
            build_executable.run(self.album_mock, Namespace(
                solution=pkg_resources.resource_filename('test_package.resources.test_solution', 'solution.py'),
                output_path=self.tmp_dir.name))
        except Exception as e:
            raise RuntimeError("Error in executable building") from e
        finally:
            if platform.system() == 'Windows':
                self.assertTrue(Path(self.tmp_dir.name).joinpath("album_import_unittest_0_1_0_installer.exe").is_file())
            else:
                self.assertTrue(Path(self.tmp_dir.name).joinpath("album_import_unittest_0_1_0_installer").is_file())

    def test_album_installation(self):
        # prepare
        tmp_env = os.environ.copy()
        album_env_path = Path(self.album_dir).joinpath('envs', 'album')
        if platform.system() == 'Windows':
            installer = Path(self.tmp_dir.name).joinpath("album_installer.exe")
            mamba_exe = Path(self.mamba_dir).joinpath('Library', 'bin', 'micromamba.exe')
            tmp_env["USERPROFILE"] = str(self.tmp_dir.name)
        else:
            installer = Path(self.tmp_dir.name).joinpath("album_installer")
            mamba_exe = Path(self.mamba_dir).joinpath('bin', 'micromamba')
            tmp_env["HOME"] = str(self.tmp_dir.name)

        print("MAMBA EXE IN INSTALLER TEST: %s" % mamba_exe)
        print(Path(mamba_exe).is_file())
        print("ALbum env paTH INSTALLER TEST: %s" % album_env_path)
        print(Path(album_env_path).is_dir())

        # call
        build_executable.run(self.album_mock, Namespace(solution=None, output_path=self.tmp_dir.name))
        cmd = subprocess.run([installer], env=tmp_env)
        album_test_cmd = subprocess.run([mamba_exe, 'run', '-p', album_env_path, 'album', '--version'])


        # assert
        self.assertFalse(cmd.returncode, "Installationprocess exited with returncode != 0")
        self.assertTrue(Path(mamba_exe).is_file(), "micromamba executable not found!")
        self.assertTrue(Path(album_env_path).is_dir(), "Album environmanet not found!")
        self.assertFalse(album_test_cmd.returncode, "Album environment not functional(version call threw error)")








if __name__ == '__main__':
    unittest.main()
