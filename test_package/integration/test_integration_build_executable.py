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
        tmp_env["MAMBA_ROOT_PREFIX"] = str(Path(self.mamba_dir))
        if platform.system() == 'Windows':
            installer = Path(self.tmp_dir.name).joinpath("album_installer.exe")
            mamba_exe = Path(self.mamba_dir).joinpath('Library', 'bin', 'micromamba.exe')
            tmp_env["USERPROFILE"] = str(self.tmp_dir.name)
        else:
            installer = Path(self.tmp_dir.name).joinpath("album_installer")
            mamba_exe = Path(self.mamba_dir).joinpath('bin', 'micromamba')
            tmp_env["HOME"] = str(self.tmp_dir.name)

        # call
        build_executable.run(self.album_mock, Namespace(solution=None, output_path=self.tmp_dir.name))
        cmd = subprocess.run([installer], env=tmp_env)
        if platform.system() == "Windows":
            pwsh_str = "%s run -p %s album --version" % (mamba_exe, album_env_path)
            album_test_cmd = subprocess.run(["powershell", "-Command", pwsh_str], capture_output=True)
        else:
            album_test_cmd = subprocess.run([mamba_exe, 'run', '-p', album_env_path, 'album', '--version'], capture_output=True)


        # assert
        self.assertFalse(cmd.returncode, "Installationprocess exited with returncode != 0")
        self.assertTrue(Path(mamba_exe).is_file(), "micromamba executable not found!")
        self.assertTrue(Path(album_env_path).is_dir(), "Album environmanet not found!")
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
        else:
            installer = Path(self.tmp_dir.name).joinpath("album_import_unittest_0_1_0_installer")
            mamba_exe = Path(self.mamba_dir).joinpath('bin', 'micromamba')
            tmp_env["HOME"] = str(self.tmp_dir.name)

        # call
        build_executable.run(self.album_mock, Namespace(
            solution=pkg_resources.resource_filename('test_package.resources.test_solution', 'solution.py'),
            output_path=self.tmp_dir.name))

        if platform.system() == "Windows":
            cmd = subprocess.run(["powershell", "-Command", installer], env=tmp_env, capture_output=True)
        else:
            cmd = subprocess.run([installer], env=tmp_env)

        if platform.system() == "Windows":
            pwsh_str = "%s run -p %s album --version" % (mamba_exe, album_env_path)
            album_test_cmd = subprocess.run(["powershell", "-Command", pwsh_str], env=tmp_env, capture_output=True)
            pwsh_sol_str = "%s run -p %s album info album:import_unittest:0.1.0" % (mamba_exe, album_env_path)
            solution_test_cmd = subprocess.run(["powershell", "-Command", pwsh_sol_str], env=tmp_env, capture_output=True)
            print(solution_test_cmd.returncode)
            print(solution_test_cmd.stdout.decode())
            print(solution_test_cmd.stderr.decode())
            #uninstall_str = "%s run -p %s album uninstall album:import_unittest:0.1.0" % (mamba_exe, album_env_path)
            #uninstall_cmd = subprocess.run(["powershell", "-Command", uninstall_str], env=tmp_env, capture_output=True)
            #print(uninstall_cmd.returncode)
            #print(uninstall_cmd.stdout.decode())
            #print(uninstall_cmd.stderr.decode())


        else:
            album_test_cmd = subprocess.run([mamba_exe, 'run', '-p', album_env_path, 'album', '--version'], capture_output=True)
            solution_test_cmd = subprocess.run(
                [mamba_exe, 'run', '-p', album_env_path, 'album', 'info', 'album:import_unittest:0.1.0'], env=tmp_env, capture_output=True)


        # assert
        self.assertFalse(cmd.returncode, "Installationprocess exited with returncode != 0")
        self.assertTrue(Path(mamba_exe).is_file(), "micromamba executable not found!")
        self.assertTrue(Path(album_env_path).is_dir(), "Album environmanet not found!")
        self.assertFalse(album_test_cmd.returncode, "Album environment not functional(version call threw error)")
        self.assertFalse(solution_test_cmd.returncode, "Solution seems not to be installed.(info solution threw error)")


if __name__ == '__main__':
    unittest.main()
