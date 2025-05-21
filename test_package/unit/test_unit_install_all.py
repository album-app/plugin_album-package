import platform
from importlib.resources import files
from pathlib import Path
from unittest.mock import patch


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
