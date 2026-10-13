import io
import os
import platform
import subprocess
import sys
from contextlib import redirect_stderr, redirect_stdout
from importlib.resources import files
from pathlib import Path
from unittest.mock import patch

import requests

from album.package import install_all
from test_package.test_common import TestCommon


class TestUnitInstallAll(TestCommon):

    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_get_album_base_path(self):
        # prepare
        album_base_path = Path.home().joinpath('.album')

        # call
        script_album_base_path = install_all.get_album_base_path()

        # assert
        self.assertEqual(album_base_path, script_album_base_path, "The album base path is not returned correctly")

    def test_get_album_env_path(self):
        # prepare
        album_env_path = Path.home().joinpath('.album', 'envs', 'album')

        # call
        script_album_env_path = install_all.get_album_env_path(Path.home().joinpath('.album'))

        # assert
        self.assertEqual(album_env_path, script_album_env_path, "The album environment path is not returned correctly")

    def test_get_mamba_exe(self):
        # prepare
        if platform.system() == 'Windows':
            mamba_exe = str(Path.home().joinpath('.album', 'micromamba', 'Library', 'bin', 'micromamba.exe'))
        else:
            mamba_exe = str(Path.home().joinpath('.album', 'micromamba', 'bin', 'micromamba'))

        # call
        script_mamba_exe = install_all.get_mamba_exe(Path.home().joinpath('.album', 'micromamba'))

        # assert
        self.assertEqual(mamba_exe, script_mamba_exe, "The path to the micromamba executable is not returned correctly")

    @patch("os.path.realpath")
    def test_read_solution_info(self, realpath):
        # prepare
        solution_info = ["<solution_placeholder>"]  # "<solution_placeholder>\nalbum:import-unittest:0.1.0"
        realpath.return_value = str(files('album.package').joinpath('solution_info.txt'))
        # call
        script_solution_info = install_all.read_solution_info()

        # assert
        self.assertEqual(solution_info, script_solution_info, "The solution info was not read correctly.")

    def test_is_downloadable(self):
        # prepare
        working_download_link = "https://gitlab.com/album-app/album/-/raw/main/album.yml"
        wrong_download_link = "https://gitlab.com"

        # call and assert
        self.assertTrue(install_all.is_downloadable(working_download_link),
                        "The downloadable check for a working link didn't return True.")
        self.assertFalse(install_all.is_downloadable(wrong_download_link),
                         "The downloadable check for a wrong link didn't return False.")

    def test_download_ressource(self):
        # prepare
        download_link = "https://gitlab.com/album-app/album/-/raw/main/album.yml"
        download_path = Path(self.tmp_dir.name).joinpath("download_test.yml")

        # call
        downloaded_file = install_all.download_resource(download_link, download_path)

        # assert
        self.assertTrue(Path(downloaded_file).is_file(), "The download_ressource function didn't download a file.")

    def test_force_remove(self):
        # prepare
        del_dir = Path(self.tmp_dir.name).joinpath("del_test")
        del_dir_read = Path(self.tmp_dir.name).joinpath("del_test_read")

        Path.mkdir(del_dir)  # accessible dir
        Path.mkdir(del_dir_read, 0o444)  # readonly dir

        # call
        install_all.force_remove(del_dir)
        install_all.force_remove(del_dir_read)

        # assert
        self.assertFalse(Path(del_dir).is_dir(), 'The directory to be deleted was NOT deleted!')
        self.assertFalse(Path(del_dir_read).is_dir(), 'The read_only directory to be deleted was NOT deleted!')

    def _create_bundle(self, bundled_solution="solution", coordinates="album:import-unittest:0.1.0"):
        """creates a directory looking like the extracted bundle of a solution installer (sys._MEIPASS)"""
        bundle_dir = Path(self.tmp_dir.name).joinpath("_MEI12345")
        bundle_dir.joinpath("solution", "data").mkdir(parents=True)
        bundle_dir.joinpath("solution", "solution.py").write_text("# solution")
        bundle_dir.joinpath("solution", "data", "model.txt").write_text("model")
        bundle_dir.joinpath("solution_info.txt").write_text("%s\n%s" % (bundled_solution, coordinates))
        return bundle_dir

    def test_get_bundle_path(self):
        # prepare
        bundle_dir = self._create_bundle()

        # call and assert
        with patch.object(sys, "_MEIPASS", str(bundle_dir), create=True):
            self.assertEqual(bundle_dir, install_all.get_bundle_path())

    def test_get_bundle_path_not_frozen(self):
        # prepare
        self.assertFalse(hasattr(sys, "_MEIPASS"))

        # call and assert
        self.assertEqual(Path(os.path.realpath(install_all.__file__)).parent, install_all.get_bundle_path())

    def test_read_solution_info_bundle(self):
        # prepare
        bundle_dir = self._create_bundle()

        # call
        with patch.object(sys, "_MEIPASS", str(bundle_dir), create=True):
            script_solution_info = install_all.read_solution_info()

        # assert
        self.assertEqual(["solution", "album:import-unittest:0.1.0"], script_solution_info)

    def test_copy_bundled_solution_dir(self):
        # prepare
        bundle_dir = self._create_bundle()
        target = self.album_dir.joinpath("packaged_solutions", "album_import-unittest_0.1.0")
        target.mkdir(parents=True)
        target.joinpath("stale.txt").write_text("left over from a previous installation")

        # call
        with patch.object(sys, "_MEIPASS", str(bundle_dir), create=True):
            solution_path = install_all.copy_bundled_solution(
                "solution", "album:import-unittest:0.1.0", self.album_dir
            )

        # assert
        self.assertEqual(target, solution_path)
        self.assertEqual("# solution", target.joinpath("solution.py").read_text())
        self.assertEqual("model", target.joinpath("data", "model.txt").read_text())
        self.assertFalse(target.joinpath("stale.txt").exists())

    def test_copy_bundled_solution_file(self):
        # prepare
        bundle_dir = self._create_bundle()
        bundle_dir.joinpath("solution", "my_solution.py").write_text("# single file solution")

        # call
        with patch.object(sys, "_MEIPASS", str(bundle_dir), create=True):
            solution_path = install_all.copy_bundled_solution(
                "solution/my_solution.py", "album:import-unittest:0.1.0", self.album_dir
            )

        # assert
        self.assertEqual(
            self.album_dir.joinpath("packaged_solutions", "album_import-unittest_0.1.0", "my_solution.py"),
            solution_path,
        )
        self.assertEqual("# single file solution", solution_path.read_text())

    def test_copy_bundled_solution_missing(self):
        # prepare
        bundle_dir = Path(self.tmp_dir.name).joinpath("_MEI_empty")
        bundle_dir.mkdir()

        # call and assert
        with patch.object(sys, "_MEIPASS", str(bundle_dir), create=True):
            with self.assertRaises(install_all.InstallationError):
                install_all.copy_bundled_solution("solution", "album:import-unittest:0.1.0", self.album_dir)

    @patch("album.package.install_all.subprocess.run")
    def test_check_for_installed_album(self, run_mock):
        # bytes output (as returned without text=True) used to make this check always fail
        for stderr in [b"", ""]:
            run_mock.return_value = subprocess.CompletedProcess([], 0, stdout=stderr, stderr=stderr)
            self.assertTrue(install_all.check_for_installed_album("env", "mamba"))
        # warnings on stderr do not mean that album is not working
        run_mock.return_value = subprocess.CompletedProcess([], 0, stdout="", stderr="warning: something")
        self.assertTrue(install_all.check_for_installed_album("env", "mamba"))
        for stderr in [b"error", "error"]:
            run_mock.return_value = subprocess.CompletedProcess([], 1, stdout="", stderr=stderr)
            self.assertFalse(install_all.check_for_installed_album("env", "mamba"))

        run_mock.assert_called_with(
            ["mamba", "run", "-p", "env", "album", "index"], capture_output=True, text=True, errors="replace"
        )

    @patch("album.package.install_all.subprocess.run")
    def test_check_for_installed_gui(self, run_mock):
        for stderr in [b"", "", "warning: something"]:
            run_mock.return_value = subprocess.CompletedProcess([], 0, stdout="", stderr=stderr)
            self.assertTrue(install_all.check_for_installed_gui("env", "mamba"))
        for stderr in [b"error", "error"]:
            run_mock.return_value = subprocess.CompletedProcess([], 2, stdout="", stderr=stderr)
            self.assertFalse(install_all.check_for_installed_gui("env", "mamba"))

        run_mock.assert_called_with(
            ["mamba", "run", "-p", "env", "album", "gui", "-h"], capture_output=True, text=True, errors="replace"
        )

    @patch("album.package.install_all.subprocess.run")
    def test_install_solution(self, run_mock):
        # prepare
        run_mock.return_value = subprocess.CompletedProcess([], 0, stdout="", stderr="")

        # call
        install_all.install_solution("mamba", "env", Path("solution_dir"))

        # assert
        self.assertEqual(
            ["mamba", "run", "-p", "env", "album", "install", "solution_dir"], run_mock.call_args[0][0]
        )

    @patch("album.package.install_all.subprocess.run")
    def test_install_solution_failure(self, run_mock):
        for returncode in [1, 2]:
            # prepare
            run_mock.return_value = subprocess.CompletedProcess([], returncode, stdout="", stderr="it broke")

            # call and assert
            with self.assertRaises(install_all.InstallationError) as context:
                install_all.install_solution("mamba", "env", "solution_dir")
            self.assertIn("it broke", str(context.exception))

    @patch("album.package.install_all.subprocess.run")
    def test_install_solution_failure_shows_stdout_and_stderr(self, run_mock):
        # prepare: album logs its errors to stdout, unrelated warnings may be printed to stderr
        run_mock.return_value = subprocess.CompletedProcess(
            [], 1, stdout="album command failed: X", stderr="warning: Y"
        )

        # call and assert
        with self.assertRaises(install_all.InstallationError) as context:
            install_all.install_solution("mamba", "env", "solution_dir")
        self.assertIn("album command failed: X", str(context.exception))
        self.assertIn("warning: Y", str(context.exception))

    def test_get_process_output(self):
        # prepare
        stdout = "\n".join("line %s" % i for i in range(50))

        # call
        output = install_all._get_process_output(
            subprocess.CompletedProcess([], 1, stdout=stdout, stderr="warning: Y\n"), max_lines=3
        )
        empty_output = install_all._get_process_output(subprocess.CompletedProcess([], 1, stdout=None, stderr=" \n"))

        # assert
        self.assertEqual("line 47\nline 48\nline 49\nwarning: Y", output)
        self.assertEqual("", empty_output)

    @patch("album.package.install_all.check_for_installed_album", return_value=True)
    @patch("album.package.install_all.install_mamba")
    @patch("album.package.install_all.subprocess.run")
    def test_install_missing_gui(self, run_mock, install_mamba_mock, _):
        # prepare
        run_mock.return_value = subprocess.CompletedProcess([], 0, stdout="", stderr="")
        mamba_exe = install_all.get_mamba_exe(self.mamba_dir)
        install_mamba_mock.return_value = mamba_exe

        # call
        install_all._install_missing_gui(self.album_dir, self.mamba_dir, "env", "album-gui", "None")

        # assert
        install_mamba_mock.assert_called_once_with(self.album_dir, self.mamba_dir)
        self.assertEqual(
            [mamba_exe, "install", "--yes", "-p", "env", "album-gui", "-c", "conda-forge"],
            run_mock.call_args[0][0],
        )

    @patch("album.package.install_all.check_for_installed_album", return_value=True)
    @patch("album.package.install_all.install_mamba")
    @patch("album.package.install_all.subprocess.run")
    def test_install_missing_gui_dev_mode(self, run_mock, install_mamba_mock, _):
        # prepare
        run_mock.return_value = subprocess.CompletedProcess([], 0, stdout="", stderr="")
        mamba_exe = install_all.get_mamba_exe(self.mamba_dir)
        Path(mamba_exe).parent.mkdir(parents=True)
        Path(mamba_exe).touch()

        # call
        install_all._install_missing_gui(
            self.album_dir, self.mamba_dir, "env", "album-gui", "None", album_dev_mode="-c constraints.txt"
        )

        # assert
        install_mamba_mock.assert_not_called()
        calls = [c[0][0] for c in run_mock.call_args_list]
        self.assertEqual(
            [
                [mamba_exe, "install", "--yes", "-p", "env", "git", "pip", "-c", "conda-forge"],
                [mamba_exe, "run", "-p", "env", "pip", "install", "album-gui", "-c", "constraints.txt"],
            ],
            calls,
        )

    @patch("album.package.install_all.check_for_installed_album", return_value=True)
    @patch("album.package.install_all.install_mamba")
    @patch("album.package.install_all.subprocess.run")
    def test_install_missing_gui_failure(self, run_mock, install_mamba_mock, _):
        # prepare
        run_mock.return_value = subprocess.CompletedProcess(
            [], 1, stdout="critical libmamba: no gui for you", stderr="warning: something"
        )
        install_mamba_mock.return_value = install_all.get_mamba_exe(self.mamba_dir)

        # call and assert
        with self.assertRaises(install_all.InstallationError) as context:
            install_all._install_missing_gui(self.album_dir, self.mamba_dir, "env", "album-gui", "None")
        self.assertIn("no gui for you", str(context.exception))
        self.assertIn("warning: something", str(context.exception))

    def _patch_main(self, bundle_dir):
        """patches everything main() would do on the system, returns the started patchers"""
        mamba_exe = install_all.get_mamba_exe(self.mamba_dir)
        Path(mamba_exe).parent.mkdir(parents=True)
        Path(mamba_exe).touch()
        patchers = {
            "meipass": patch.object(sys, "_MEIPASS", str(bundle_dir), create=True),
            "get_album_base_path": patch(
                "album.package.install_all.get_album_base_path", return_value=self.album_dir
            ),
            "install_mamba": patch("album.package.install_all.install_mamba"),
            "check_for_installed_album": patch(
                "album.package.install_all.check_for_installed_album", return_value=True
            ),
            "check_for_installed_gui": patch(
                "album.package.install_all.check_for_installed_gui", return_value=True
            ),
            "check_for_solution": patch("album.package.install_all.check_for_solution", return_value=False),
            "install_solution": patch("album.package.install_all.install_solution"),
            "_install_album_full": patch("album.package.install_all._install_album_full", return_value=True),
            "create_shortcut": patch("album.package.install_all.create_shortcut"),
        }
        mocks = {}
        for key, patcher in patchers.items():
            mocks[key] = patcher.start()
            self.addCleanup(patcher.stop)
        return mamba_exe, mocks

    def test_main_installs_bundled_solution(self):
        # prepare
        mamba_exe, mocks = self._patch_main(self._create_bundle())
        packaged_solution = self.album_dir.joinpath("packaged_solutions", "album_import-unittest_0.1.0")
        album_env_path = str(install_all.get_album_env_path(str(self.album_dir)))

        def install_solution(*args):
            self.assertTrue(packaged_solution.joinpath("solution.py").is_file())
            self.assertTrue(packaged_solution.joinpath("data", "model.txt").is_file())

        mocks["install_solution"].side_effect = install_solution

        # call
        install_all.main()

        # assert
        mocks["install_solution"].assert_called_once_with(mamba_exe, album_env_path, str(packaged_solution))
        self.assertFalse(packaged_solution.exists(), "The copy of the solution was not removed after the installation.")
        self.assertFalse(self.album_dir.joinpath("packaged_solutions").exists())
        mocks["_install_album_full"].assert_not_called()
        mocks["install_mamba"].assert_not_called()
        mocks["create_shortcut"].assert_called_once()

    def test_main_installs_bundled_solution_with_album(self):
        # prepare: no working album installation, album, album gui and the solution get installed in one go
        mamba_exe, mocks = self._patch_main(self._create_bundle())
        mocks["check_for_installed_album"].return_value = False
        packaged_solution = self.album_dir.joinpath("packaged_solutions", "album_import-unittest_0.1.0")

        def install_album_full(*args, **kwargs):
            self.assertTrue(Path(args[4]).joinpath("solution.py").is_file())
            return True

        mocks["_install_album_full"].side_effect = install_album_full

        # call
        install_all.main()

        # assert
        mocks["_install_album_full"].assert_called_once()
        self.assertEqual(str(packaged_solution), mocks["_install_album_full"].call_args[0][4])
        mocks["install_solution"].assert_not_called()
        self.assertFalse(packaged_solution.exists(), "The copy of the solution was not removed after the installation.")
        mocks["create_shortcut"].assert_called_once()

    def test_main_solution_already_installed(self):
        # prepare
        mamba_exe, mocks = self._patch_main(self._create_bundle())
        mocks["check_for_solution"].return_value = True
        packaged_solutions = self.album_dir.joinpath("packaged_solutions")
        other_copy = packaged_solutions.joinpath("album_other_0.1.0")
        other_copy.mkdir(parents=True)

        # call
        install_all.main()

        # assert
        mocks["install_solution"].assert_not_called()
        self.assertFalse(packaged_solutions.joinpath("album_import-unittest_0.1.0").exists())
        self.assertTrue(other_copy.is_dir(), "Copies of other solutions must not be removed.")
        mocks["create_shortcut"].assert_called_once()

    @patch("album.package.install_all.force_remove")
    def test_remove_packaged_solution_failure(self, force_remove_mock):
        # prepare
        force_remove_mock.side_effect = PermissionError("in use")
        stdout = io.StringIO()

        # call
        with redirect_stdout(stdout):
            install_all.remove_packaged_solution("album:import-unittest:0.1.0", self.album_dir)

        # assert: a failing clean up does not fail the installation
        self.assertIn("WARNING: Could not remove", stdout.getvalue())

    def test_main_installs_bundled_solution_with_missing_gui(self):
        # prepare: album is installed, album gui is missing
        mamba_exe, mocks = self._patch_main(self._create_bundle())
        mocks["check_for_installed_gui"].return_value = False
        packaged_solution = self.album_dir.joinpath("packaged_solutions", "album_import-unittest_0.1.0")
        album_env_path = str(install_all.get_album_env_path(str(self.album_dir)))

        # call
        with patch("album.package.install_all._install_missing_gui") as install_missing_gui_mock:
            install_all.main()

        # assert
        install_missing_gui_mock.assert_called_once()
        self.assertEqual(str(packaged_solution), install_missing_gui_mock.call_args[0][4])
        mocks["_install_album_full"].assert_not_called()
        mocks["install_solution"].assert_called_once_with(mamba_exe, album_env_path, str(packaged_solution))

    def test_main_album_only(self):
        # prepare
        mamba_exe, mocks = self._patch_main(self._create_bundle("None", "None"))

        # call
        install_all.main()

        # assert
        self.assertEqual("None", mocks["_install_album_full"].call_args[0][4])
        mocks["install_solution"].assert_not_called()
        self.assertFalse(self.album_dir.joinpath("packaged_solutions").exists())

    def test_run_failing_solution_installation(self):
        # prepare
        mamba_exe, mocks = self._patch_main(self._create_bundle())
        mocks["install_solution"].side_effect = install_all.InstallationError("album install failed")
        stdout = io.StringIO()
        stderr = io.StringIO()

        # call
        with self.assertRaises(SystemExit) as context:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                install_all.run()

        # assert
        self.assertEqual(1, context.exception.code)
        self.assertIn("album install failed", stderr.getvalue())
        self.assertNotIn("Installation successfully finished.", stdout.getvalue())
        mocks["create_shortcut"].assert_not_called()
        # the copy is kept, so the solution can be installed manually
        self.assertTrue(
            self.album_dir.joinpath("packaged_solutions", "album_import-unittest_0.1.0", "solution.py").is_file()
        )

    def test_run_failing_installation_steps(self):
        # prepare
        mamba_exe, mocks = self._patch_main(self._create_bundle("None", "None"))
        errors = [
            subprocess.CalledProcessError(1, ["micromamba", "create"]),
            ConnectionError("Could not connect to resource https://micro.mamba.pm"),
            requests.exceptions.ConnectionError("Max retries exceeded"),
            NotImplementedError("There is no micromamba version for your processor architecture riscv64."),
        ]
        for error in errors:
            with self.subTest(error=repr(error)):
                mocks["_install_album_full"].side_effect = error
                stdout = io.StringIO()
                stderr = io.StringIO()

                # call
                with self.assertRaises(SystemExit) as context:
                    with redirect_stdout(stdout), redirect_stderr(stderr):
                        install_all.run()

                # assert
                self.assertEqual(1, context.exception.code)
                self.assertIn("ERROR: %s" % error, stderr.getvalue())
                self.assertIn("Installation failed.", stderr.getvalue())
                self.assertNotIn("Installation successfully finished.", stdout.getvalue())
                mocks["create_shortcut"].assert_not_called()

    def test_run_unexpected_error(self):
        # prepare
        mamba_exe, mocks = self._patch_main(self._create_bundle("None", "None"))
        mocks["_install_album_full"].side_effect = ValueError("bug")

        # call and assert: unexpected errors keep their traceback
        with self.assertRaises(ValueError):
            with redirect_stdout(io.StringIO()):
                install_all.run()
