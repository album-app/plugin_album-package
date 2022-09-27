import os
import platform
from pathlib import Path

from album.package import install_mamba
from test_package.test_common import TestCommon


class TestUnitInstallMamba(TestCommon):

    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_set_mamba_env_var(self):
        # prepare
        mamba_test_path = self.mamba_dir
        if platform.system() == 'Windows':
            mamba_test_exe = Path(mamba_test_path).joinpath('Library', 'bin', 'micromamba.exe')
        else:
            mamba_test_exe = Path(mamba_test_path).joinpath('bin', 'micromamba')

        # call
        install_mamba._set_mamba_env_vars(mamba_test_path)

        # assert
        self.assertEqual(str(mamba_test_path), os.getenv('MAMBA_ROOT_PREFIX'),
                         "Error when setting Mamba_root_prefix env var")
        self.assertEqual(str(mamba_test_exe), os.getenv('MAMBA_EXE'), "Error when setting mamba_exe env var")

    def test_get_mamba_exe(self):
        # prepare
        if platform.system() == 'Windows':
            mamba_test_exe = Path(self.mamba_dir).joinpath('Library', 'bin', 'micromamba.exe')
        else:
            mamba_test_exe = Path(self.mamba_dir).joinpath('bin', 'micromamba')

        # call
        script_mamba_exe = install_mamba.get_mamba_exe(self.mamba_dir)

        # assert
        self.assertEqual(mamba_test_exe, script_mamba_exe, "Path to mamba executable was not returned correctly.")

    def test_download_mamba(self):
        # prepare
        test_mamba_base_path = self.mamba_dir

        # call
        mamba_installer = install_mamba._download_mamba(test_mamba_base_path)

        # assert
        self.assertTrue(Path(mamba_installer).is_file(), "The mamba installer was not downloaded.")
