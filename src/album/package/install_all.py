import errno
import logging
import os.path
import platform
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from album.package.install_mamba import install_mamba

full_install = False


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


def _install_missing_gui(album_base_path, mamba_base_path, album_env_path, album_gui_url, yml_path, solution):
    # install album gui and if needed mamba
    print("Found album, but not album gui. Installing album gui...")
    # check for mamba
    mamba_exe = get_mamba_exe(mamba_base_path)
    if not Path(mamba_exe).is_file():
        mamba_exe = install_mamba(album_base_path, mamba_base_path)

    if check_for_installed_album(album_env_path, mamba_exe):
        cmd = subprocess.run([mamba_exe, "run", "-p", album_env_path, "pip", "install", album_gui_url])
        if cmd.returncode == 0:
            print("Successfully installed album gui.")
        else:
            print("There was an error installing album gui: %s" % cmd.stderr)
    else:
        _install_album_full(album_base_path, mamba_base_path, album_env_path, album_gui_url, yml_path, solution)


def _install_album_full(album_base_path, mamba_base_path, album_env_path, album_gui_url, yml_path, solution):
    global full_install
    full_install = True
    if (solution == "None") and Path(album_env_path).is_dir():
        print("Removing old album environment...")
        force_remove(album_env_path)

    # install album and album gui and if needed micromamba
    if not Path(album_base_path).is_dir():
        Path(album_base_path).mkdir()

    mamba_exe = get_mamba_exe(mamba_base_path)
    if not Path(mamba_base_path).is_file():
        print("Conda command not available. Installing Miniconda into " + str(mamba_base_path))
        if not Path(mamba_base_path).is_dir():
            Path(mamba_base_path).mkdir()

        install_mamba(album_base_path, mamba_base_path)

    print("Installing album into %s..." % album_env_path)

    a = subprocess.run([mamba_exe, 'create', '-p', album_env_path, '-f', yml_path], capture_output=True)

    if a.returncode == 0:
        print("Successfully installed album.")
        print("Installing album gui...")
        g = subprocess.run([mamba_exe, 'run', '-p', album_env_path, 'pip', 'install', album_gui_url])
        if g.returncode == 0:
            print("Successfully installed album gui.")
        else:
            print("An error occurred installing album gui: %s" % g.stderr)
        if solution != "None":
            print("Installing the solution...")
            install_solution(mamba_exe, album_env_path, solution)
    else:
        print("An error occurred installing album: %s" % a.stderr)
        sys.exit()


def check_for_installed_album(album_env_path, mamba_exe):
    try:
        cmd = subprocess.run([mamba_exe, "run", "-p", album_env_path, "album", "-h"], capture_output=True)
        if cmd.returncode == 0:
            return True
        else:
            return False
    except Exception as e:
        if Path(album_env_path).is_dir():
            answer = input("There seems to be a broken album environment at %s. "
                           "Do you want to delete it to be able to install a new album environment? (y/n)" % album_env_path)
            while True:
                if answer == 'y' or answer == 'yes':
                    print("Deleting broken album environment...")
                    shutil.rmtree(album_env_path)
                    break
                elif answer == 'n' or answer == 'no':
                    break
                else:
                    answer = input("Invalid choise please enter y/yes or n/no.")
        return False


def check_for_installed_gui(album_env_path, mamba_exe):
    # check if album gui is installed in the album environment installed via this script
    try:
        cmd = subprocess.run([mamba_exe, "run", "-p", album_env_path, "album", "gui", "-h"], capture_output=True)
        if cmd.returncode == 0:
            return True
        else:
            return False
    except Exception:
        return False


def install_solution(mamba_exe, album_env_path, solution):
    try:
        cmd = subprocess.run([mamba_exe, "run", "-p", album_env_path, "album", "install", Path(str(solution))],
                             capture_output=True)
    except Exception as e:
        print("An error occurred installing the solution: %s" % cmd.stderr)
        sys.exit()


def check_for_solution(mamba_exe, album_env_path, solution):
    try:
        cmd = subprocess.run([mamba_exe, "run", "-p", album_env_path, "album", "info", Path(solution)],
                             capture_output=True)
        if cmd.returncode == 0:
            return True
        else:
            return False
    except Exception:
        return False


def force_remove(path, warning=True):
    path = Path(path)
    if path.exists():
        try:
            if path.is_file():
                try:
                    path.unlink()
                except PermissionError:
                    handle_remove_readonly(os.unlink, path, sys.exc_info())
            else:
                shutil.rmtree(
                    str(path), ignore_errors=False, onerror=handle_remove_readonly
                )
        except PermissionError as e:
            logging.warning("Cannot delete %s." % str(path))
            if not warning:
                raise e


def handle_remove_readonly(func, path, exc):
    """Changes readonly flag of a given path."""
    excvalue = exc[1]
    if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise


def create_shortcut(mamba_exe, album_env_path):
    p = subprocess.Popen([mamba_exe, 'run', '-p', album_env_path, 'album', 'add-shortcut'], stdout=sys.stdout,
                         stderr=sys.stderr)
    p.communicate()


def get_album_base_path():
    return Path.home().joinpath('.album')


def get_album_env_path(album_base_path):
    return Path(album_base_path).joinpath("envs", "album")


def get_mamba_exe(mamba_base_path):
    if platform.system() == 'Windows':
        return Path(mamba_base_path).joinpath('Library', 'bin', 'micromamba.exe')
    else:
        return Path(mamba_base_path).joinpath('bin', 'micromamba')


def read_solution_info():
    with open(Path(os.path.realpath(__file__)).parent.joinpath('solution_info.txt'), 'r') as file:
        sol_info = file.read()
    return str(sol_info)


def main():
    album_base_path = str(get_album_base_path())
    # conda_path = Path(album_base_path).joinpath("Miniconda")
    # conda_exe = get_conda_exe(conda_path)
    mamba_base_path = Path(album_base_path).joinpath("micromamba")
    mamba_exe = get_mamba_exe(mamba_base_path)
    album_env_path = str(get_album_env_path(album_base_path))
    album_gui_url = "https://gitlab.com/album-app/plugins/album-gui/-/archive/main/album-gui-main.zip"
    yml_url = "https://gitlab.com/album-app/album/-/raw/main/album.yml"
    solution = read_solution_info()
    global full_install

    if not Path(album_base_path).is_dir():
        Path(album_base_path).mkdir()

    yml_path = download_resource(yml_url, Path(album_base_path).joinpath('album.yml'))

    print("Checking for micromamba installation...")
    if not Path(mamba_exe).is_file():
        install_mamba(album_base_path, mamba_base_path)

    if not check_for_installed_album(album_env_path, mamba_exe) or (solution == "None"):
        _install_album_full(album_base_path, mamba_base_path, album_env_path, album_gui_url, yml_path, solution)

    if not full_install:
        print("Checking for album gui installation...")
        if not check_for_installed_gui(album_env_path, mamba_exe):
            _install_missing_gui(album_base_path, mamba_base_path, album_env_path, album_gui_url, yml_path, solution)

        if solution != "None":
            print("Checking if the solution is installed...")
            if not check_for_solution(mamba_exe, album_env_path, solution):
                install_solution(mamba_exe, album_env_path, solution)

    create_shortcut(mamba_exe, album_env_path)

    print("Installation successfully finished.")


if __name__ == '__main__':
    main()
