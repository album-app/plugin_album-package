import os.path
import platform
import subprocess
from pathlib import Path
import wget


def _install_conda_windows(conda_path):
    # install miniconda for windows
    conda_url_win = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
    conda_installer = Path(conda_path).joinpath("Miniconda_install.exe")
    wget.download(conda_url_win, str(conda_installer))
    cmd = "Start-Process %s -argumentlist \"/InstallationType=JustMe /S /D=%s\" -wait" % (
        conda_installer, conda_path)
    install_process = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    conda_exe = str(Path(conda_path).joinpath("condabin", "conda.bat"))

    if install_process.returncode != 0:
        print("An error occured when installing Conda: %s" % install_process.stderr)
    else:
        print("Successfully installed Miniconda.")

    return conda_exe


def _install_conda_linux(conda_path):
    # install miniconda for linux
    conda_url_linux = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    conda_installer = Path(conda_path).joinpath("Miniconda_install.sh")
    wget.download(conda_url_linux, str(conda_installer))
    install_process = subprocess.run(["bash", conda_installer, "-b", "-u", "-p", conda_path, ">", "/dev/null"],
                                     capture_output=True)
    conda_exe = str(Path(conda_path).joinpath("condabin", "conda"))
 # TODO: HIER NOCHMAL NACH CONDA INFO CHECKEN!!!
    if install_process.returncode != 0:
        print("An error occured when installing Conda: %s" % install_process.stderr)
    else:
        print("Successfully installed Miniconda.")

    return conda_exe


def _install_conda_macos(conda_path):
    # install miniconda for macos
    conda_url_macos = "https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
    conda_installer = Path(conda_path).joinpath("Miniconda_install.sh")
    wget.download(conda_url_macos, str(conda_installer))
    install_process = subprocess.run(["bash", conda_installer, "-b", "-u", "-p", conda_path, ">", "/dev/null"],
                                     capture_output=True)
    conda_exe = str(Path(conda_path).joinpath("condabin", "conda"))

    if install_process.returncode != 0:
        print("An error occured when installing Conda: %s" % install_process.stderr)
    else:
        print("Successfully installed Miniconda.")

    return conda_exe


def _install_missing_gui(album_base_path, conda_path, album_env_path, album_gui_url):
    #install album gui and if needed conda
    print("Found album, but not album gui. Installing album gui...")
    # check for conda
    if check_for_preinstalled_conda():
        conda_exe = "conda"
    elif check_for_script_installed_conda(conda_path):
        if platform.system() == 'Windows':
            conda_exe = str(Path(album_base_path).joinpath('Miniconda', 'condabin', 'conda.exe'))
        else:
            conda_exe = str(Path(album_base_path).joinpath('Miniconda', 'condabin', 'conda'))
    else:
        conda_exe = _install_missing_conda(conda_path)

    if check_for_preinstalled_album(conda_path):
        subprocess.run([conda_exe, "run", "-n", "album", "pip", "install", album_gui_url])
    else:
        subprocess.run([conda_exe, "run", "-p", album_env_path, "pip", "install", album_gui_url])


def _install_missing_conda(conda_path):
    # install miniconda
    print(
        "Found album but could not find a working conda installation. Installing conda into: %s" % conda_path)
    if not os.path.isdir(conda_path):
        os.mkdir(conda_path)

    if platform.system() == 'Windows':
        conda_exe = _install_conda_windows(conda_path)

    elif platform.system() == 'Linux':
        conda_exe = _install_conda_linux(conda_path)

    elif platform.system() == 'Darwin':
        conda_exe = _install_conda_macos(conda_path)
    else:
        print("Your OS is currently not supported")
        raise NotImplementedError
    return conda_exe


def _install_album_full(album_base_path, conda_path, album_env_path, album_gui_url, yml_path):
    #install album and album gui and if needed miniconda
    print("Could not find album. Checking for conda installation....")
    if not os.path.isdir(album_base_path):
        os.mkdir(album_base_path)

    if check_for_preinstalled_conda():
        print("Conda Command available.")
        conda_exe = "conda"
    elif check_for_script_installed_conda(conda_path):
        if platform.system() == 'Windows':
            print("Conda Command available.")
            conda_exe = str(Path(album_base_path).joinpath('Miniconda', 'condabin', 'conda.exe'))
        else:
            print("Conda Command available.")
            conda_exe = str(Path(album_base_path).joinpath('Miniconda', 'condabin', 'conda'))
    else:
        print("Conda command not available. Installing Miniconda into " + str(conda_path))
        if not os.path.isdir(conda_path):
            os.mkdir(conda_path)

        if platform.system() == 'Windows':
            conda_exe = _install_conda_windows(conda_path)

        elif platform.system() == 'Linux':
            conda_exe = _install_conda_linux(conda_path)

        elif platform.system() == 'Darwin':
            conda_exe = _install_conda_macos(conda_path)
        else:
            print("Your OS is currently not supported")
            raise NotImplementedError

    print("-------------------------")

    print("Installing album...")

    a = subprocess.run([conda_exe, 'env', 'create', '-p', album_env_path, '-f', yml_path], capture_output=True)

    if a.returncode == 0:
        print("Successfully installed album.")
        print("Installing album gui...")
        g = subprocess.run([conda_exe, 'run', '-p', album_env_path, 'pip', 'install', album_gui_url])
        if g.returncode == 0:
            print("Successfully installed album gui.")
        else:
            print("An error occured installing album gui:")
            print(g.stderr)
    else:
        print("An error occured installing album:")
        print(a.stderr)


def check_for_preinstalled_album(conda_path):
    try:
        cmd = subprocess.run(["conda", "run", "-n", "album", "album", "-h"], capture_output=True)
        return True
    except Exception:
        try:
            if platform.system() == 'Windows':
                cmd = subprocess.run([str(Path(conda_path).joinpath('condabin', 'conda.exe')), "run", "-n", "album", "album", "-h"], capture_output=True)
                if cmd.returncode == 0:
                    return True
            else:
                cmd = subprocess.run([Path(conda_path).joinpath('condabin', 'conda'), "run", "-n", "album", "album", "-h"], capture_output=True)
                if cmd.returncode == 0:
                    return True
        except Exception:
            return False


def check_for_script_installed_album(album_env_path,conda_path):
    try:
        cmd = subprocess.run(["conda", "run", "-p", album_env_path, "album", "-h"], capture_output=True)
        return True
    except Exception:
        try:
            if platform.system() == 'Windows':
                cmd = subprocess.run(
                    [Path(conda_path).joinpath('condabin', 'conda.exe'), "run", "-p", album_env_path, "album", "-h"], capture_output=True)
                if cmd.returncode == 0:
                    return True
            else:
                cmd = subprocess.run(
                    [Path(conda_path).joinpath('condabin', 'conda'), "run", "-p", album_env_path, "album", "-h"], capture_output=True)
                if cmd.returncode == 0:
                    return True
        except Exception:
            return False


def check_for_preinstalled_gui(conda_path):
    # check if album gui is installed in the preinstalled album
    print("Checking for preinstalled album gui installation...")
    try:
        cmd = subprocess.run(["conda", "run", "-n", "album", "album", "gui", "-h"], capture_output=True)
        return True
    except Exception:
        try:
            if platform.system() == 'Windows':
                cmd = subprocess.run(
                    [Path(conda_path).joinpath('condabin', 'conda.exe'), "run", "-n", "album", "album", "gui", "-h"], capture_output=True)
                if cmd.returncode == 0:
                    return True
            else:
                cmd = subprocess.run(
                    [Path(conda_path).joinpath('condabin', 'conda'), "run", "-n", "album", "album", "gui", "-h"], capture_output=True)
                if cmd.returncode == 0:
                    return True
        except Exception:
            return False


def check_for_script_installed_gui(album_env_path,conda_path):
    # check if album gui is installed in the album installed via this script
    try:
        cmd = subprocess.run(["conda", "run", "-p", album_env_path, "album", "gui", "-h"], capture_output=True)
        return True
    except Exception:
        try:
            if platform.system() == 'Windows':
                cmd = subprocess.run(
                    [Path(conda_path).joinpath('condabin', 'conda.exe'), "run", "-p", album_env_path, "album", "gui", "-h"], capture_output=True)
                if cmd.returncode == 0:
                    return True
            else:
                cmd = subprocess.run(
                    [Path(conda_path).joinpath('condabin', 'conda'), "run", "-p", album_env_path, "album", "gui", "-h"], capture_output=True)
                if cmd.returncode == 0:
                    return True
        except Exception:
            return False


    try:
        print("Checking for script installed album gui installation...")
        cmd = subprocess.run(["conda", "run", "-p", album_env_path, "album", "gui", "-h"], capture_output=True)
        return True
    except Exception:
        return False


def check_for_preinstalled_conda():
    try:
        print("Checking for preinstalled conda installation...")
        cmd = subprocess.run(["conda", "info"], capture_output=True)
        return True
    except Exception:
        return False


def check_for_script_installed_conda(conda_path):
    print("Checking for script installed conda installation...")
    if platform.system() == 'Windows':
        conda_exe = str(Path(conda_path).joinpath('condabin', 'conda.exe'))
    else:
        conda_exe = str(Path(conda_path).joinpath('condabin', 'conda'))

    return os.path.isfile(Path(conda_exe))


def main():
    album_base_path = str(Path.home().joinpath('.album'))
    _conda_path = str(Path(album_base_path).joinpath("Miniconda"))
    album_env_path = str(Path(album_base_path).joinpath('envs', 'album'))
    album_gui_url = "https://gitlab.com/album-app/plugins/album-gui/-/archive/main/album-gui-main.zip"
    yml_url = "https://gitlab.com/album-app/album/-/raw/main/album.yml"
    yml_path = str(Path(os.path.realpath(__file__)).parent.joinpath('album.yml'))
    print(yml_path)
    #check if yml file is present
    if not os.path.isfile(yml_path):
        print("Downloading album yml file")
        yml_path = Path(album_base_path).joinpath('album.yml')
        wget(yml_url, Path(yml_path))

    print("Checking for album installation...")
    if (not check_for_preinstalled_album(_conda_path)) and (not check_for_script_installed_album(album_env_path, _conda_path)):

        _install_album_full(album_base_path, _conda_path, album_env_path, album_gui_url, yml_path)

    elif (not check_for_preinstalled_gui(_conda_path)) and (not check_for_script_installed_gui(album_env_path, _conda_path)):

        _install_missing_gui(album_base_path, _conda_path, album_env_path, album_gui_url)

    elif (not check_for_preinstalled_conda()) and (not check_for_script_installed_conda(_conda_path)):

        _install_missing_conda(_conda_path)


    print("END INSTALL SCRIPT!!")



if __name__ == '__main__':
    main()
