import os
import platform
import subprocess
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

    def test_build_album_installer(self):
        # call
        build_executable.run(self.album_mock, Namespace(solution=None, output_path=self.tmp_dir.name))

        # assert
        if platform.system() == 'Windows':
            self.assertTrue(Path(self.tmp_dir.name).joinpath("album_installer.exe").is_file())
        elif platform.system() == 'Darwin':
            self.assertTrue(Path(self.tmp_dir.name).joinpath("album_installer.app").is_file())
        else:
            self.assertTrue(Path(self.tmp_dir.name).joinpath("album_installer").is_file())

    def test_build_solution_installer(self):
        # call
        build_executable.run(self.album_mock, Namespace(
            solution=pkg_resources.resource_filename('test_package.resources.test_solution', 'solution.py'),
            output_path=self.tmp_dir.name))

        # assert
        if platform.system() == 'Windows':
            self.assertTrue(Path(self.tmp_dir.name).joinpath("album_import_unittest_0_1_0_installer.exe").is_file())
        elif platform.system() == 'Darwin':
            self.assertTrue(Path(self.tmp_dir.name).joinpath("album_import_unittest_0_1_0_installer.app").is_file())
        else:
            self.assertTrue(Path(self.tmp_dir.name).joinpath("album_import_unittest_0_1_0_installer").is_file())

    def test_album_installation(self):
        # prepare
        tmp_env = os.environ.copy()
        album_env_path = Path(self.album_dir).joinpath('envs', 'album')
        tmp_env["MAMBA_ROOT_PREFIX"] = str(Path(self.mamba_dir))
        if platform.system() == 'Windows':
            installer = Path(self.tmp_dir.name).joinpath("album_installer.exe")
            mamba_exe = Path(self.mamba_dir).joinpath('Library', 'bin', 'micromamba.exe')
            tmp_env["USERPROFILE"] = str(self.tmp_dir.name)
        elif platform.system() == 'Darwin':
            installer = Path(self.tmp_dir.name).joinpath("album_installer.app")
            mamba_exe = Path(self.mamba_dir).joinpath('bin', 'micromamba')
            tmp_env["HOME"] = str(self.tmp_dir.name)
        else:
            installer = Path(self.tmp_dir.name).joinpath("album_installer")
            mamba_exe = Path(self.mamba_dir).joinpath('bin', 'micromamba')
            tmp_env["HOME"] = str(self.tmp_dir.name)

        # call
        build_executable.run(self.album_mock, Namespace(solution=None, output_path=self.tmp_dir.name))
        cmd = subprocess.run([str(installer)], env=tmp_env, check=True)

        # assert
        # assert
        self.assertFalse(cmd.returncode, f"Installationprocess exited with returncode != 0")
        self.assertTrue(Path(mamba_exe).is_file(), "micromamba executable not found!")
        self.assertTrue(Path(album_env_path).is_dir(), "Album environmanet not found!")

        # get album version
        if platform.system() == "Windows":
            pwsh_str = "%s run -p %s album --version" % (mamba_exe, album_env_path)
            album_test_cmd = subprocess.run(["powershell", "-Command", pwsh_str], check=True)
        else:
            album_test_cmd = subprocess.run([str(mamba_exe), 'run', '-p', str(album_env_path), 'album', '--version', '--log', 'DEBUG'], check=True)

        # assert
        self.assertFalse(album_test_cmd.returncode, "Album environment not functional(version call threw error)")

    def test_solution_installation(self):
        # prepare
        tmp_env = os.environ.copy()
        album_env_path = Path(self.album_dir).joinpath('envs', 'album')
        tmp_env["MAMBA_ROOT_PREFIX"] = str(Path(self.mamba_dir))
        if platform.system() == 'Windows':
            installer = Path(self.tmp_dir.name).joinpath("album_import_unittest_0_1_0_installer.exe")
            mamba_exe = Path(self.mamba_dir).joinpath('Library', 'bin', 'micromamba.exe')
            tmp_env["USERPROFILE"] = str(self.tmp_dir.name)
        elif platform.system() == 'Darwin':
            installer = Path(self.tmp_dir.name).joinpath("album_import_unittest_0_1_0_installer.app")
            mamba_exe = Path(self.mamba_dir).joinpath('bin', 'micromamba')
            tmp_env["HOME"] = str(self.tmp_dir.name)
        else:
            installer = Path(self.tmp_dir.name).joinpath("album_import_unittest_0_1_0_installer")
            mamba_exe = Path(self.mamba_dir).joinpath('bin', 'micromamba')
            tmp_env["HOME"] = str(self.tmp_dir.name)

        # call
        build_executable.run(self.album_mock, Namespace(
            solution=pkg_resources.resource_filename('test_package.resources.test_solution', 'solution.py'),
            output_path=self.tmp_dir.name))
        if platform.system() == "Windows":
            cmd = subprocess.run(["powershell", "-Command", installer], env=tmp_env, check=True)
        else:
            cmd = subprocess.run([str(installer)], env=tmp_env, check=True)
        
        # assert
        self.assertFalse(cmd.returncode, f"Installationprocess exited with returncode != 0")
        self.assertTrue(Path(mamba_exe).is_file(), "micromamba executable not found!")
        self.assertTrue(Path(album_env_path).is_dir(), "Album environmanet not found!")

        if platform.system() == "Windows":
            pwsh_str = "%s run -p %s album --version" % (mamba_exe, album_env_path)
            album_test_cmd = subprocess.run(["powershell", "-Command", pwsh_str], env=tmp_env, check=True)
            pwsh_sol_str = "%s run -p %s album info album:import_unittest:0.1.0" % (mamba_exe, album_env_path)
            solution_test_cmd = subprocess.run(["powershell", "-Command", pwsh_sol_str], env=tmp_env, check=True)

        else:
            album_test_cmd = subprocess.run([mamba_exe, 'run', '-p', album_env_path, 'album', '--version'], check=True)
            solution_test_cmd = subprocess.run(
                [mamba_exe, 'run', '-p', album_env_path, 'album', 'info', 'album:import_unittest:0.1.0'], env=tmp_env, check=True)

        self.assertFalse(album_test_cmd.returncode, "Album environment not functional(version call threw error)")
        self.assertFalse(solution_test_cmd.returncode, "Solution seems not to be installed.(info solution threw error)")


if __name__ == '__main__':
    unittest.main()
