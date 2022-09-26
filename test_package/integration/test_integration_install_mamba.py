import os
import platform
from pathlib import Path
from unittest.mock import patch

from album.package import install_mamba
from test_package.test_common import TestCommon


class TestIntegrationInstallMamba(TestCommon):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_unpack_mamba(self):
        # prepare
        mamba_test_path = Path(self.tmp_dir.name).joinpath('micromamba')
        if platform.system() == 'Windows':
            mamba_test_exe = Path(mamba_test_path).joinpath('Library', 'bin', 'micromamba.exe')
        else:
            mamba_test_exe = Path(mamba_test_path).joinpath('bin', 'micromamba')

        # call
        if platform.system() == 'Windows':
            install_mamba._unpack_mamba_win(install_mamba._download_mamba(mamba_test_path), mamba_test_path)
        else:
            install_mamba._unpack_mamba_unix(install_mamba._download_mamba(mamba_test_path), mamba_test_path)

        # assert
        self.assertTrue(Path(mamba_test_exe).is_file(), "Error when unpacking mamba.")

    @patch('album.package.install_mamba._init_pwsh')
    @patch('album.package.install_mamba._init_bash')
    @patch('album.package.install_mamba._init_zsh')
    def test_install_mamba(self, pwsh_mock, bash_mock, zsh_mock):
        # prepare
        album_test_path = Path(self.tmp_dir.name).joinpath('.album')
        mamba_test_path = Path(album_test_path).joinpath('micromamba')
        if platform.system() == 'Windows':
            mamba_test_exe = Path(mamba_test_path).joinpath('Library', 'bin', 'micromamba.exe')
        else:
            mamba_test_exe = Path(mamba_test_path).joinpath('bin', 'micromamba')

        # call
        install_mamba.install_mamba(album_test_path, mamba_test_path)

        # assert
        self.assertTrue(Path(mamba_test_exe).is_file(), "No mamba executable found!")
        self.assertEqual(str(mamba_test_path), os.getenv('MAMBA_ROOT_PREFIX'),
                         "Error when setting Mamba_root_prefix env var")
        self.assertEqual(str(mamba_test_exe), os.getenv('MAMBA_EXE'), "Error when setting mamba_exe env var")

