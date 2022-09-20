import logging
import platform
import subprocess
import sys
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


def get_conda_executable(base_dir):
    if platform.system() == 'Windows':
        conda_exe = str(Path(base_dir).joinpath('condabin', 'conda.bat'))
    else:
        conda_exe = str(Path(base_dir).joinpath('condabin', 'conda'))
    return conda_exe


def install_conda_if_missing(_conda_path, album_base_path):
    conda_executable = get_conda_executable(_conda_path)
    if not check_for_script_installed_conda(conda_executable):
        _install_missing_conda(_conda_path, album_base_path)
    return conda_executable


def check_for_script_installed_conda(conda_exe):
    return Path(conda_exe).is_file()


def _install_missing_conda(conda_path, album_base_path):
    # install miniconda
    print(
        "Could not find a working conda installation. Installing conda into: %s" % conda_path)
    if not Path(conda_path).is_dir():
        if not Path(album_base_path).is_dir():
            Path(album_base_path).mkdir()
        Path(conda_path).mkdir()

    if platform.system() == 'Windows':
        conda_exe = _install_conda_windows(conda_path)

    elif platform.system() == 'Linux':
        conda_exe = _install_conda_linux(conda_path)

    elif platform.system() == 'Darwin':
        conda_exe = _install_conda_macos(conda_path)
    else:
        logging.error("Your OS is currently not supported")
        raise NotImplementedError
    return conda_exe


def _install_conda_windows(conda_path):
    # install miniconda for windows
    conda_url_win = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
    conda_installer = Path(conda_path).joinpath("Miniconda_install.exe")
    download_resource(conda_url_win, conda_installer)

    cmd = "Start-Process %s -argumentlist \"/InstallationType=JustMe /S /D=%s\" -wait" % (
        conda_installer, conda_path)
    install_process = subprocess.Popen(["powershell", "-Command", cmd], stdout=sys.stdout, stderr=sys.stderr)
    install_process.communicate()
    conda_exe = Path(conda_path).joinpath("condabin", "conda.bat")
    conda_exe = str(conda_exe)

    try:
        cmd = subprocess.Popen([conda_exe, "info"], stdout=sys.stdout, stderr=sys.stderr)
        cmd.communicate()
        print("Successfully installed Miniconda.")
        return conda_exe
    except Exception:
        logging.error("An error occured when installing Conda: %s" % install_process.stderr)
        return conda_exe


def _install_conda_linux(conda_path):
    # install miniconda for linux
    conda_url_linux = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    conda_installer = Path(conda_path).joinpath("Miniconda_install.sh")
    download_resource(conda_url_linux, conda_installer)

    install_process = subprocess.Popen(['sh', conda_installer, "-b", "-u", "-p", conda_path],
                                       stdout=sys.stdout, stderr=sys.stderr)
    install_process.communicate()
    conda_exe = str(Path(conda_path).joinpath("condabin", "conda"))
    try:
        cmd = subprocess.Popen([conda_exe, "info"], stdout=sys.stdout, stderr=sys.stderr)
        cmd.communicate()
        print("Successfully installed Miniconda.")
        return conda_exe
    except Exception:
        logging.error("An error occured when installing Conda: %s" % install_process.stderr)
        return conda_exe


def _install_conda_macos(conda_path):
    # install miniconda for macos
    conda_url_macos = "https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
    conda_installer = Path(conda_path).joinpath("Miniconda_install.sh")

    download_resource(conda_url_macos, conda_installer)

    install_process = subprocess.Popen(["bash", conda_installer, "-b", "-u", "-p", conda_path, ">", "/dev/null"],
                         stdout=sys.stdout, stderr=sys.stderr)
    install_process.communicate()
    conda_exe = str(Path(conda_path).joinpath("condabin", "conda"))

    try:
        cmd = subprocess.Popen([conda_exe, "info"],
                         stdout=sys.stdout, stderr=sys.stderr)
        cmd.communicate()
        print("Successfully installed Miniconda.")
        return conda_exe
    except Exception:
        logging.error("An error occured when installing Conda: %s" % install_process.stderr)
        return conda_exe


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
