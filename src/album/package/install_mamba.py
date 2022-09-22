import os
import platform
import subprocess
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


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
    print(path)
    with open(path, "wb") as f:
        for chunk in r:
            f.write(chunk)

    return path


def _install_7_zip(mamba_base_path):
    zip_url = "https://www.7-zip.org/a/7z2201-x64.exe"
    zip_installer = download_resource(zip_url, Path(mamba_base_path).joinpath('7z_installer.exe'))
    install_process = subprocess.run([zip_installer, '/S'], capture_output=True)
    return install_process.returncode


def check_architecture():
    check = subprocess.run(['uname', '-m'], capture_output=True)
    return check.stdout


def get_7z_exe():
    return Path(os.getenv('ProgramFiles')).joinpath('7-Zip', '7z.exe')


def _download_mamba(mamba_base_path):
    if platform.system() == 'Windows':
        return _download_mamba_win(Path(mamba_base_path).joinpath('micromamba.tar.bz2'))
    elif platform.system() == 'Darwin':
        return _download_mamba_macos(Path(mamba_base_path).joinpath('micromamba.tar'))
    elif platform.system() == 'Linux':
        return _download_mamba_linux(Path(mamba_base_path).joinpath('micromamba.tar'))
    else:
        raise NotImplementedError("Your operating system is currently not supported.")


def _download_mamba_win(mamba_installer_path):
    return download_resource("https://micro.mamba.pm/api/micromamba/win-64/latest", mamba_installer_path)


def _download_mamba_macos(mamba_installer_path):
    if check_architecture() == 'x86_64':
        return download_resource("https://micro.mamba.pm/api/micromamba/osx-64/latest", mamba_installer_path)
    elif check_architecture().lower() == 'arm64':
        return download_resource("https://micro.mamba.pm/api/micromamba/osx-arm64/latest", mamba_installer_path)
    else:
        raise NotImplementedError("There is no micromamba version for your processor architecture.")


def _download_mamba_linux(mamba_installer_path):
    if check_architecture() == 'x86_64':
        return download_resource("https://micro.mamba.pm/api/micromamba/linux-64/latest", mamba_installer_path)
    elif check_architecture().lower() == 'arm64':
        return download_resource("https://micro.mamba.pm/api/micromamba/linux-aarch64/latest", mamba_installer_path)
    elif check_architecture().lower() == 'power':
        return download_resource("https://micro.mamba.pm/api/micromamba/linux-ppc64le/latest", mamba_installer_path)
    else:
        raise NotImplementedError("There is no micromamba version for your processor architecture.")


def _unpack_mamba_win(mamba_installer, mamba_base_path):
    zip_exe = get_7z_exe()
    unzip_process_1 = subprocess.run([zip_exe, 'x', mamba_installer, '-aoa', '-o%s' % mamba_base_path],
                                     capture_output=True)
    mamba_installer = Path(mamba_base_path).joinpath(Path(mamba_installer).stem)
    unzip_process_2 = subprocess.run(
        [zip_exe, 'x', mamba_installer, '-ttar', '-aoa', '-r', 'Library\\bin\\micromamba.exe',
         '-o%s' % mamba_base_path], capture_output=True)
    # TODO: Success Check?


def _unpack_mamba_unix(mamba_installer, mamba_base_path):
    tar_process = subprocess.run(['tar', '-xvjf', mamba_installer, '-C', mamba_base_path, 'bin/micromamba'])


def _set_mamba_env_vars(mamba_base_path):
    os.environ['MAMBA_ROOT_PREFIX'] = str(mamba_base_path)
    os.environ['MAMBA_EXE'] = str(get_mamba_exe(mamba_base_path))


def _init_pwsh(mamba_base_path):
    mamba_exe = get_mamba_exe(mamba_base_path)
    init_process = subprocess.run([mamba_exe, 'shell', 'init', '-s', 'powershell', '-p', mamba_base_path],
                                  capture_output=True)


def _init_bash(mamba_base_path):
    mamba_exe = get_mamba_exe(mamba_base_path)
    init_process = subprocess.run([mamba_exe, 'shell', 'init', '-s', 'bash', '-p', mamba_base_path],
                                  capture_output=True)


def _init_zsh(mamba_base_path):
    mamba_exe = get_mamba_exe(mamba_base_path)
    init_process = subprocess.run([mamba_exe, 'shell', 'init', '-s', 'bash', '-p', mamba_base_path],
                                  capture_output=True)


def get_mamba_exe(mamba_base_path):
    if platform.system() == 'Windows':
        return Path(mamba_base_path).joinpath('Library', 'bin', 'micromamba.exe')
    else:
        return Path(mamba_base_path).joinpath('bin', 'micromamba')


def _install_mamba_windows(mamba_base_path):
    _install_7_zip(mamba_base_path)
    mamba_installer = _download_mamba(mamba_base_path)
    _unpack_mamba_win(mamba_installer, mamba_base_path)
    _set_mamba_env_vars(mamba_base_path)
    _init_pwsh(mamba_base_path)


def _install_mamba_linux(mamba_base_path):
    mamba_installer = _download_mamba(mamba_base_path)
    _unpack_mamba_unix(mamba_installer, mamba_base_path)
    _set_mamba_env_vars(mamba_base_path)
    _init_bash(mamba_base_path)


def _install_mamba_macos(mamba_base_path):
    mamba_installer = _download_mamba(mamba_base_path)
    _unpack_mamba_unix(mamba_installer, mamba_base_path)
    _set_mamba_env_vars(mamba_base_path)
    _init_zsh(mamba_base_path)


def install_mamba(album_base_path, mamba_base_path):
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
