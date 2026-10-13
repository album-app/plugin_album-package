import os
import platform
from pathlib import Path
from unittest.mock import patch

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
            mamba_test_exe = str(Path(self.mamba_dir).joinpath('Library', 'bin', 'micromamba.exe'))
        else:
            mamba_test_exe = str(Path(self.mamba_dir).joinpath('bin', 'micromamba'))

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

    @patch('album.package.install_mamba.download_resource')
    @patch('album.package.install_mamba.check_architecture')
    def test_download_mamba_linux_architecture(self, check_architecture_mock, download_resource_mock):
        # "uname -m" reports aarch64 and ppc64le on linux
        for architecture, link in [('x86_64', install_mamba.MAMBA_LINK_LINUX_X86_64),
                                   ('aarch64', install_mamba.MAMBA_LINK_LINUX_ARM64),
                                   ('arm64', install_mamba.MAMBA_LINK_LINUX_ARM64),
                                   ('ppc64le', install_mamba.MAMBA_LINK_LINUX_POWER),
                                   ('power', install_mamba.MAMBA_LINK_LINUX_POWER)]:
            # prepare
            check_architecture_mock.return_value = architecture
            download_resource_mock.reset_mock()

            # call
            install_mamba._download_mamba_linux('micromamba.tar')

            # assert
            download_resource_mock.assert_called_once_with(link, 'micromamba.tar')

        check_architecture_mock.return_value = 's390x'
        with self.assertRaises(NotImplementedError):
            install_mamba._download_mamba_linux('micromamba.tar')

    @patch('album.package.install_mamba.download_resource')
    @patch('album.package.install_mamba.check_architecture')
    def test_download_mamba_macos_architecture(self, check_architecture_mock, download_resource_mock):
        for architecture, link in [('x86_64', install_mamba.MAMBA_LINK_MACOS_X86_64),
                                   ('arm64', install_mamba.MAMBA_LINK_MACOS_ARM64)]:
            # prepare
            check_architecture_mock.return_value = architecture
            download_resource_mock.reset_mock()

            # call
            install_mamba._download_mamba_macos('micromamba.tar')

            # assert
            download_resource_mock.assert_called_once_with(link, 'micromamba.tar')

        check_architecture_mock.return_value = 'ppc64le'
        with self.assertRaises(NotImplementedError):
            install_mamba._download_mamba_macos('micromamba.tar')

    @patch('album.package.install_mamba._install_mamba_macos')
    @patch('album.package.install_mamba._install_mamba_linux')
    @patch('album.package.install_mamba._install_mamba_windows')
    def test_install_mamba_returns_mamba_exe(self, *_):
        # call
        mamba_exe = install_mamba.install_mamba(self.album_dir, self.mamba_dir)

        # assert
        self.assertEqual(install_mamba.get_mamba_exe(self.mamba_dir), mamba_exe)
