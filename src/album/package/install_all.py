import errno
import logging
import os.path
import platform
import shutil
import stat
import subprocess
import sys
from pathlib import Path

from album.package.install_conda import install_conda_if_missing

full_install = False

def _install_missing_gui(album_base_path, conda_path, album_env_path, album_gui_url, yml_path, solution):
    # install album gui and if needed conda
    print("Found album, but not album gui. Installing album gui...")
    # check for conda
    conda_exe = get_conda_exe(conda_path)
    if not Path(conda_exe).is_file():
        conda_exe = install_conda_if_missing(conda_path, album_base_path)

    if check_for_installed_album(album_env_path, conda_exe):
        cmd = subprocess.run([conda_exe, "run", "-p", album_env_path, "pip", "install", album_gui_url])
        if cmd.returncode == 0:
            print("Successfully installed album gui.")
        else:
            print("There was an error installing album gui: %s" % cmd.stderr)
    else:
        _install_album_full(album_base_path, conda_path, album_env_path, album_gui_url, yml_path, solution)


def _install_album_full(album_base_path, conda_path, album_env_path, album_gui_url, yml_path, solution):
    global full_install
    full_install = True
    if (solution == "None") and Path(album_env_path).is_dir():
        print("Removing old album environment...")
        force_remove(album_env_path)

    # install album and album gui and if needed miniconda
    if not Path(album_base_path).is_dir():
        Path(album_base_path).mkdir()

    conda_exe = get_conda_exe(conda_path)
    if not Path(conda_exe).is_file():
        print("Conda command not available. Installing Miniconda into " + str(conda_path))
        if not Path(conda_path).is_dir():
            Path(conda_path).mkdir()

        install_conda_if_missing(conda_path, album_base_path)

    print("Installing album into %s..." % album_env_path)

    a = subprocess.run([conda_exe, 'env', 'create', '-p', album_env_path, '-f', yml_path], capture_output=True)

    if a.returncode == 0:
        print("Successfully installed album.")
        print("Installing album gui...")
        g = subprocess.run([conda_exe, 'run', '-p', album_env_path, 'pip', 'install', album_gui_url])
        if g.returncode == 0:
            print("Successfully installed album gui.")
        else:
            print("An error occurred installing album gui: %s" % g.stderr)
        if solution != "None":
            print("Installing the solution...")
            install_solution(conda_exe, album_env_path, solution)
    else:
        print("An error occurred installing album: %s" % a.stderr)
        sys.exit()


def check_for_installed_album(album_env_path, conda_exe):
    try:
        if platform.system() == 'Windows':
            cmd = subprocess.run([conda_exe, "run", "-p", album_env_path, "album", "-h"], capture_output=True)
            if cmd.returncode == 0:
                return True
            else:
                return False
        else:
            cmd = subprocess.run([conda_exe, "run", "-p", album_env_path, "album", "-h"], capture_output=True)
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


def check_for_installed_gui(album_env_path, conda_exe):
    # check if album gui is installed in the album installed via this script
    try:
        if platform.system() == 'Windows':
            cmd = subprocess.run([conda_exe, "run", "-p", album_env_path, "album", "gui", "-h"], capture_output=True)
            if cmd.returncode == 0:
                return True
            else:
                return False
        else:
            cmd = subprocess.run([conda_exe, "run", "-p", album_env_path, "album", "gui", "-h"], capture_output=True)
            if cmd.returncode == 0:
                return True
            else:
                return False
    except Exception:
        return False


def check_for_installed_conda(conda_exe):
    return Path(conda_exe).is_file()


def install_solution(conda_exe, album_env_path, solution):
    try:
        cmd = subprocess.run([conda_exe, "run", "-p", album_env_path, "album", "install", Path(str(solution))],
                             capture_output=True)
    except Exception as e:
        print("An error occurred installing the solution: %s" % cmd.stderr)
        sys.exit()


def check_for_solution(conda_exe, album_env_path, solution):
    try:
        cmd = subprocess.run([conda_exe, "run", "-p", album_env_path, "album", "info", Path(solution)],
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


def create_shortcut(conda_exe, album_env_path):
    p = subprocess.Popen([conda_exe, 'run', '-p', album_env_path, 'album', 'add-shortcut'], stdout=sys.stdout,
                         stderr=sys.stderr)
    p.communicate()


def get_album_base_path():
    return Path.home().joinpath('.album')


def get_album_env_path(album_base_path):
    return Path(album_base_path).joinpath("envs", "album")


def get_conda_exe(conda_path):
    if platform.system() == 'Windows':
        conda_exe = str(Path(conda_path).joinpath('condabin', 'conda.bat'))
    else:
        conda_exe = str(Path(conda_path).joinpath('condabin', 'conda'))

    return conda_exe


def read_solution_info():
    with open(Path(os.path.realpath(__file__)).parent.joinpath('solution_info.txt'), 'r') as file:
        sol_info = file.read()
    return str(sol_info)


def main():
    album_base_path = str(get_album_base_path())
    conda_path = Path(album_base_path).joinpath("Miniconda")
    conda_exe = get_conda_exe(conda_path)
    album_env_path = str(get_album_env_path(album_base_path))
    album_gui_url = "https://gitlab.com/album-app/plugins/album-gui/-/archive/main/album-gui-main.zip"
    yml_path = "https://gitlab.com/album-app/album/-/raw/main/album.yml"
    solution = read_solution_info()
    global full_install

    print("Checking for conda installation...")
    if not Path(conda_exe).is_file():
        install_conda_if_missing(conda_path, album_base_path)

    print("Checking for album installation...")
    if not check_for_installed_album(album_env_path, conda_exe) or (solution == "None"):
        _install_album_full(album_base_path, conda_path, album_env_path, album_gui_url, yml_path, solution)

    if not full_install:
        print("Checking for album gui installation...")
        if not check_for_installed_gui(album_env_path, conda_exe):
            _install_missing_gui(album_base_path, conda_path, album_env_path, album_gui_url, yml_path, solution)

        if solution != "None":
            print("Checking if the solution is installed...")
            if not check_for_solution(conda_exe, album_env_path, solution):
                install_solution(conda_exe, album_env_path, solution)

    create_shortcut(conda_exe, album_env_path)

    print("Installation successfully finished.")


if __name__ == '__main__':
    main()
