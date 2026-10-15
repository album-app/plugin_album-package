import os
import platform
import subprocess
from pathlib import Path
import tarfile

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# NOTE: Using `latest` is possible, but we pin the version to ensure compatibility.
MAMBA_LINK_LINUX_X86_64 = "https://micro.mamba.pm/api/micromamba/linux-64/2.5.0"
MAMBA_LINK_LINUX_ARM64 = "https://micro.mamba.pm/api/micromamba/linux-aarch64/2.5.0"
MAMBA_LINK_LINUX_POWER = "https://micro.mamba.pm/api/micromamba/linux-ppc64le/2.5.0"

MAMBA_LINK_MACOS_X86_64 = "https://micro.mamba.pm/api/micromamba/osx-64/2.5.0"
MAMBA_LINK_MACOS_ARM64 = "https://micro.mamba.pm/api/micromamba/osx-arm64/2.5.0"

MAMBA_LINK_WINDOWS = "https://micro.mamba.pm/api/micromamba/win-64/2.5.0"


def is_downloadable(url):
    """Shows if url is a downloadable resource."""
    with _get_session() as s:
        h = s.head(url, allow_redirects=True)
        header = h.headers
        content_type = header.get("content-type")
        if "html" in content_type.lower():
            return False
        return True


def _get_session():
    s = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)

    adapter = HTTPAdapter(max_retries=retry)

    s.mount("http://", adapter)
    s.mount("https://", adapter)

    return s


def _request_get(url):
    """Get a response from a request to a resource url."""
    with _get_session() as s:
        r = s.get(url, allow_redirects=True, stream=True)

        if r.status_code != 200:
            raise ConnectionError("Could not connect to resource %s!" % url)

        return r


def download_resource(url, path):
    """Downloads a resource given its url."""
    path = Path(path)

    if not is_downloadable(url):
        raise AssertionError('Resource "%s" not downloadable!' % url)

    r = _request_get(url)
    with open(path, "wb") as f:
        for chunk in r:
            f.write(chunk)

    return path


def check_architecture():
    """checks the processor architecture of the system"""
    check = subprocess.run(['uname', '-m'], capture_output=True)
    return check.stdout.decode().rstrip()


def _download_mamba(mamba_base_path):
    """downloads micromamba"""
    if platform.system() == 'Windows':
        return _download_mamba_win(Path(mamba_base_path).joinpath('micromamba.tar.bz2'))
    elif platform.system() == 'Darwin':
        return _download_mamba_macos(Path(mamba_base_path).joinpath('micromamba.tar'))
    elif platform.system() == 'Linux':
        return _download_mamba_linux(Path(mamba_base_path).joinpath('micromamba.tar'))
    else:
        raise NotImplementedError("Your operating system is currently not supported.")


def _download_mamba_win(mamba_installer_path):
    """downloads micromamba for windows"""
    return download_resource(MAMBA_LINK_WINDOWS, mamba_installer_path)


def _download_mamba_macos(mamba_installer_path):
    """downloads micromamba for macOS depending on the processor architecture"""
    architecture = check_architecture().lower()
    if architecture == 'x86_64':
        return download_resource(MAMBA_LINK_MACOS_X86_64, mamba_installer_path)
    elif architecture == 'arm64':
        return download_resource(MAMBA_LINK_MACOS_ARM64, mamba_installer_path)
    else:
        raise NotImplementedError("There is no micromamba version for your processor architecture %s." % architecture)


def _download_mamba_linux(mamba_installer_path):
    """downloads micromamba for linux depending on the processor architecture"""
    # "uname -m" reports aarch64 and ppc64le on linux, arm64 and power are accepted as well for backwards compatibility
    architecture = check_architecture().lower()
    if architecture == 'x86_64':
        return download_resource(MAMBA_LINK_LINUX_X86_64, mamba_installer_path)
    elif architecture in ('aarch64', 'arm64'):
        return download_resource(MAMBA_LINK_LINUX_ARM64, mamba_installer_path)
    elif architecture in ('ppc64le', 'power'):
        return download_resource(MAMBA_LINK_LINUX_POWER, mamba_installer_path)
    else:
        raise NotImplementedError("There is no micromamba version for your processor architecture %s." % architecture)


def _unpack_mamba_win(mamba_installer, mamba_base_path):
    """unpacks the windows version of the micromamba archive (tar.bz2)"""
    with tarfile.open(Path(mamba_installer), 'r:bz2') as tar:
        tar.extractall(Path(mamba_base_path))


def _unpack_mamba_unix(mamba_installer, mamba_base_path):
    """unpacks the micromamba archives for linux and macOS"""
    with tarfile.open(mamba_installer, 'r') as tar:
        tar.extractall(mamba_base_path)


def _set_mamba_env_vars(mamba_base_path):
    """Sets the micromamba environment variables"""
    os.environ['MAMBA_ROOT_PREFIX'] = str(mamba_base_path)
    os.environ['MAMBA_EXE'] = str(get_mamba_exe(mamba_base_path))


def get_mamba_exe(mamba_base_path):
    """returns the path to the micromamba executable"""
    if platform.system() == 'Windows':
        return str(Path(mamba_base_path).joinpath('Library', 'bin', 'micromamba.exe'))
    else:
        return str(Path(mamba_base_path).joinpath('bin', 'micromamba'))


# The shell is not initialised ("micromamba shell init"): it edits ~/.bashrc, ~/.zshrc or the PowerShell profile and
# can replace an existing conda / micromamba setup. The installer, album and the Album shortcut call micromamba by its
# absolute path, command line users activate ~/.album/envs/album as described in the Album documentation.
def _install_mamba_windows(mamba_base_path):
    """installs micromamba on windows"""
    mamba_installer = _download_mamba(mamba_base_path)
    _unpack_mamba_win(mamba_installer, mamba_base_path)
    _set_mamba_env_vars(mamba_base_path)


def _install_mamba_linux(mamba_base_path):
    """installs micromamba on linux"""
    mamba_installer = _download_mamba(mamba_base_path)
    _unpack_mamba_unix(mamba_installer, mamba_base_path)
    _set_mamba_env_vars(mamba_base_path)


def _install_mamba_macos(mamba_base_path):
    """installs micromamba on macOS"""
    mamba_installer = _download_mamba(mamba_base_path)
    _unpack_mamba_unix(mamba_installer, mamba_base_path)
    _set_mamba_env_vars(mamba_base_path)


def install_mamba(album_base_path, mamba_base_path):
    """installs micromamba and returns the path to the micromamba executable"""
    if not Path(album_base_path).exists():
        Path(album_base_path).mkdir()
    if not Path(mamba_base_path).exists():
        Path(mamba_base_path).mkdir()

    if platform.system() == 'Windows':
        _install_mamba_windows(mamba_base_path)
    elif platform.system() == 'Darwin':
        _install_mamba_macos(mamba_base_path)
    elif platform.system() == 'Linux':
        _install_mamba_linux(mamba_base_path)
    else:
        raise NotImplementedError("Your operating system is currently not supported")

    return get_mamba_exe(mamba_base_path)
