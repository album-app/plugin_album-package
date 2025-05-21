import os
import platform
import subprocess
import unittest
from argparse import Namespace
from pathlib import Path

from importlib.resources import files

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
            solution=str(files('test_package.resources.test_solution').joinpath('solution.py')),
            output_path=Path(self.tmp_dir.name).joinpath('test_output')))

        self.assertTrue(Path(self.tmp_dir.name).joinpath('test_output').is_dir(),
                        "Output directory was not created.")

    def test_clean_up(self):
        # call
        build_executable.run(self.album_mock, Namespace(
            solution=str(files('test_package.resources.test_solution').joinpath('solution.py')),
            output_path=self.tmp_dir.name))

        # assert
        self.assertFalse(Path(self.tmp_dir.name).joinpath('build').is_dir(),
                         "PyInstallers build directory was not deleted.")
        self.assertFalse(
            Path(self.tmp_dir.name).joinpath('album_album_import_unittest_0_1_0_installer.spec').is_file(),
            "build_executable.spec was not deleted.")
        self.assertFalse(Path(self.tmp_dir.name).joinpath('solution_info.txt').is_file(),
                         "solution_info.txt was not deleted.")

    def test_clean_up_failing_resolve(self):
        try:
            # prepare
            self.album_mock.resolve.return_value = "Murks"

            # call
            build_executable.run(self.album_mock, Namespace(
                solution=str(files('test_package.resources.test_solution').joinpath('bla.py')),
                output_path=self.tmp_dir.name))
        except Exception:
            pass
        finally:
            # assert
            self.assertFalse(Path(self.tmp_dir.name).joinpath('build').is_dir(),
                             "PyInstallers build directory was not deleted.")
            self.assertFalse(
                Path(self.tmp_dir.name).joinpath('album_album_import_unittest_0_1_0_installer.spec').is_file(),
                "build_executable.spec was not deleted.")
            self.assertFalse(Path(self.tmp_dir.name).joinpath('solution_info.txt').is_file(),
                             "solution_info.txt was not deleted.")

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
            solution=str(files('test_package.resources.test_solution').joinpath('solution.py')),
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
        try:
            if platform.system() != "Darwin":
                print(f"Running installer: {installer.absolute()}")
                print(f"Using mamba executable: {mamba_exe.absolute()}")
                print(f"MAMBA_ROOT_PREFIX: {tmp_env['MAMBA_ROOT_PREFIX']}")

                cmd: subprocess.CompletedProcess[str] = subprocess.run([str(installer.absolute())], env=tmp_env, check=True, capture_output=True,
                                                            text=True)
            else:
                # FIXME: currently, we need to rename the macos installer app to not have the app ending in order
                #  for the runner to be able to execute it.
                # not sure if this is also problematic for the users. We are currently providing the installer.app file,
                # but testing the renamed installer file.
                installer_renamed = Path(self.tmp_dir.name).joinpath("album_import_unittest_0_1_0_installer")
                os.rename(str(installer), str(installer_renamed))

                cmd = subprocess.run([str(installer_renamed.absolute())], env=tmp_env, check=True, capture_output=True,
                                                            text=True)
        except subprocess.CalledProcessError as e:
            print(f"Command failed with return code {e.returncode}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            self.fail(e.stderr)

        # assert
        self.assertFalse(cmd.returncode, f"Installation process exited with returncode != 0")
        self.assertTrue(Path(mamba_exe).is_file(), "Micromamba executable not found!")
        self.assertTrue(Path(album_env_path).is_dir(), "Album environment not found!")

        # get album version
        if platform.system() == "Windows":
            pwsh_str = "%s run -p %s album --version" % (mamba_exe, album_env_path)
            album_test_cmd = subprocess.run(["powershell", "-Command", pwsh_str], check=True)
        else:
            album_test_cmd = subprocess.run(
                [str(mamba_exe.absolute()), 'run', '-p', str(album_env_path.absolute()), 'album', '--version', '--log',
                 'DEBUG'], check=True)

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
            solution=str(files('test_package.resources.test_solution').joinpath('solution.py')),
            output_path=self.tmp_dir.name))
        try:
            if platform.system() != "Darwin":
                cmd = subprocess.run([str(installer.absolute())], env=tmp_env, check=True, capture_output=True,
                                     text=True)
            else:
                # FIXME: currently, we need to rename the macos installer app to not have the app ending in order for the runner to be able to execute it.
                # not sure if this is also problematic for the users. We are currently providing the installer.app file, but testing the renamed installer file.
                installer_renamed = Path(self.tmp_dir.name).joinpath("album_import_unittest_0_1_0_installer")
                os.rename(str(installer), str(installer_renamed))

                cmd = subprocess.run([str(installer_renamed.absolute())], env=tmp_env, check=True, capture_output=True,
                                     text=True)
        except subprocess.CalledProcessError as e:
            print(f"Command failed with return code {e.returncode}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            self.fail(e.stderr)

        # assert
        self.assertFalse(cmd.returncode,
                         f"Installation process exited with return code != 0: \n{cmd.stdout}\n{cmd.stderr}")
        self.assertTrue(Path(mamba_exe).is_file(), "Micromamba executable not found!")
        self.assertTrue(Path(album_env_path).is_dir(), "Album environment not found!")

        # call album and solution
        if platform.system() == "Windows":
            pwsh_str = "%s run -p %s album --version" % (mamba_exe, album_env_path)
            album_test_cmd = subprocess.run(["powershell", "-Command", pwsh_str], env=tmp_env, check=True)
            pwsh_sol_str = "%s run -p %s album info album:import-unittest:0.1.0" % (mamba_exe, album_env_path)
            solution_test_cmd = subprocess.run(["powershell", "-Command", pwsh_sol_str], env=tmp_env, check=True)

        else:
            album_test_cmd = subprocess.run(
                [mamba_exe, 'run', '-p', album_env_path, 'album', '--version'], check=True
            )
            solution_test_cmd = subprocess.run(
                [mamba_exe, 'run', '-p', album_env_path, 'album', 'info', 'album:import-unittest:0.1.0'],
                env=tmp_env,
                check=True
            )

        # assert
        self.assertFalse(
            album_test_cmd.returncode, "Album environment not functional(version call threw error)"
        )
        self.assertFalse(
            solution_test_cmd.returncode, "Solution seems not to be installed.(info solution threw error)"
        )


if __name__ == '__main__':
    unittest.main()
