import os.path
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
import wget

warned = 0
deleted = False


def _install_conda_windows(conda_path):
    # install miniconda for windows
    conda_url_win = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
    conda_installer = Path(conda_path).joinpath("Miniconda_install.exe")
    wget.download(conda_url_win, str(conda_installer))
    cmd = "Start-Process %s -argumentlist \"/InstallationType=JustMe /S /D=%s\" -wait" % (
        conda_installer, conda_path)
    install_process = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    conda_exe = Path(conda_path).joinpath("condabin", "conda.bat")
    conda_exe = str(conda_exe)

    try:
        cmd = subprocess.run([conda_exe, "info"], capture_output=True)
        print("Successfully installed Miniconda.")
        return conda_exe
    except Exception:
        print("An error occured when installing Conda: %s" % install_process.stderr)
        return conda_exe


def _install_conda_linux(conda_path):
    # install miniconda for linux
    conda_url_linux = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    conda_installer = Path(conda_path).joinpath("Miniconda_install.sh")
    wget.download(conda_url_linux, str(conda_installer))
    install_process = subprocess.run(["bash", conda_installer, "-b", "-u", "-p", conda_path, ">", "/dev/null"],
                                     capture_output=True)
    conda_exe = str(Path(conda_path).joinpath("condabin", "conda"))
    try:
        cmd = subprocess.run([conda_exe, "info"], capture_output=True)
        print("Successfully installed Miniconda.")
        return conda_exe
    except Exception:
        print("An error occured when installing Conda: %s" % install_process.stderr)
        return conda_exe


def _install_conda_macos(conda_path):
    # install miniconda for macos
    conda_url_macos = "https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
    conda_installer = Path(conda_path).joinpath("Miniconda_install.sh")
    wget.download(conda_url_macos, str(conda_installer))
    install_process = subprocess.run(["bash", conda_installer, "-b", "-u", "-p", conda_path, ">", "/dev/null"],
                                     capture_output=True)
    conda_exe = str(Path(conda_path).joinpath("condabin", "conda"))

    try:
        cmd = subprocess.run([conda_exe, "info"], capture_output=True)
        print("Successfully installed Miniconda.")
        return conda_exe
    except Exception:
        print("An error occured when installing Conda: %s" % install_process.stderr)
        return conda_exe


def _install_missing_gui(album_base_path, conda_path, album_env_path, album_gui_url, yml_path):
    # install album gui and if needed conda
    print("Found album, but not album gui. Installing album gui...")
    # check for conda
    # TODO AUSLAGERN!
    if check_for_preinstalled_conda():
        conda_exe = "conda"
    elif check_for_script_installed_conda(conda_path):
        if platform.system() == 'Windows':
            conda_exe = str(Path(album_base_path).joinpath('Miniconda', 'condabin', 'conda.bat'))
        else:
            conda_exe = str(Path(album_base_path).joinpath('Miniconda', 'condabin', 'conda'))
    else:
        conda_exe = _install_missing_conda(conda_path, album_base_path)

    # FIXME: HERE THE SUCCESS OF THE INSTALL NEEDS TO BE CHECKED!!!
    if check_for_preinstalled_album(conda_path, yml_path):
        subprocess.run([conda_exe, "run", "-n", "album", "pip", "install", album_gui_url])
    elif check_for_script_installed_album(album_env_path, conda_path, yml_path):
        subprocess.run([conda_exe, "run", "-p", album_env_path, "pip", "install", album_gui_url])
    else:
        _install_album_full(album_base_path, conda_path, album_env_path, album_gui_url, yml_path)


def _install_pyshortcuts(album_base_path, album_env_path, conda_path, album_gui_url, yml_path):
    # install pyshortcuts and if needed conda
    print("Installing PyShortcuts...")
    # check for conda
    # TODO AUSLAGERN!
    if check_for_preinstalled_conda():
        conda_exe = "conda"
    elif check_for_script_installed_conda(conda_path):
        if platform.system() == 'Windows':
            conda_exe = str(Path(album_base_path).joinpath('Miniconda', 'condabin', 'conda.bat'))
        else:
            conda_exe = str(Path(album_base_path).joinpath('Miniconda', 'condabin', 'conda'))
    else:
        conda_exe = _install_missing_conda(conda_path, album_base_path)

    # FIXME: HERE THE SUCCESS OF THE INSTALL NEEDS TO BE CHECKED!!!
    if check_for_preinstalled_album(conda_path, yml_path):
        subprocess.run([conda_exe, "run", "-n", "album", "pip", "install", "pyshortcuts==1.8.2"])
    elif check_for_script_installed_album(album_env_path, conda_path, yml_path):
        subprocess.run([conda_exe, "run", "-p", album_env_path, "pip", "install", "pyshortcuts==1.8.2"])
    else:
        _install_album_full(album_base_path, conda_path, album_env_path, album_gui_url, yml_path)
    # if check_for_preinstalled_album(conda_path):


##
#    cmd = subprocess.run([conda_exe, "install", "-n", "album", '-c', 'conda-forge', '-y', "pyshortcuts==1.8.2"],
#                         capture_output=True)
#    print("SHORTCUT INSTALL OUT!!!!!!!!!! %s"%cmd.stdout)
#    print("SHORtCUT INSTALL ERR!!!!!!!!!! %s"%cmd.stderr)
# elif check_for_script_installed_album(album_env_path, conda_path):
#    subprocess.run([conda_exe, "install", "-p", album_env_path, '-c', 'conda-forge', '-y', "pyshortcuts==1.8.2"])
# else:
#    _install_album_full(album_base_path, conda_path, album_env_path, album_gui_url, yml_path)


def _install_missing_conda(conda_path, album_base_path):
    # install miniconda
    print(
        "Could not find a working conda installation. Installing conda into: %s" % conda_path)
    if not os.path.isdir(conda_path):
        if not os.path.isdir(album_base_path):
            os.mkdir(album_base_path)
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
    # install album and album gui and if needed miniconda
    if not deleted:
        print("Could not find album. Checking for conda installation....")

    if not os.path.isdir(album_base_path):
        os.mkdir(album_base_path)
    # this conda check is technically not needed anymore, since the conda check in the main happens first
    # but a double check cannot hurt and to have an install the whole thing function is good
    if check_for_preinstalled_conda():
        print("Conda Command available.")
        conda_exe = "conda"
    elif check_for_script_installed_conda(conda_path):
        if platform.system() == 'Windows':
            print("Conda Command available.")
            conda_exe = str(Path(album_base_path).joinpath('Miniconda', 'condabin', 'conda.bat'))
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

    print("Installing album into %s..." % album_env_path)

    a = subprocess.run([conda_exe, 'env', 'create', '-p', album_env_path, '-f', yml_path], capture_output=True)

    if a.returncode == 0:
        print("Successfully installed album.")
        print("Installing album gui...")
        g = subprocess.run([conda_exe, 'run', '-p', album_env_path, 'pip', 'install', album_gui_url])
        if g.returncode == 0:
            print("Successfully installed album gui.")
        else:
            print("An error occurred installing album gui:")
            print(g.stderr)
        print("Installing PyShortcuts...")
        s = subprocess.run(
            [conda_exe, 'install', '-p', album_env_path, '-c', 'conda-forge', '-y', "pyshortcuts==1.8.2"])
        if s.returncode == 0:
            print("Successfully installed pyshortcuts.")
        else:
            print("An error occurred installing pyshortcuts:")
            print(s.stderr)
    else:
        print("An error occurred installing album:")
        print(a.stderr)
        sys.exit()


def check_for_preinstalled_album(conda_path, yml_path):
    #    if not deleted:
    try:
        cmd = subprocess.run(["conda", "run", "-n", "album", "album", "-h"], capture_output=True)
        if cmd.returncode == 0:
            if warned != 2:
                album_version_check(yml_path=yml_path, conda=True, album=True, album_env_path=None,
                                    conda_path=conda_path)
                if deleted:
                    return False

            return True
        else:
            return False
    except Exception:
        try:
            if platform.system() == 'Windows':
                cmd = subprocess.run(
                    [str(Path(conda_path).joinpath('condabin', 'conda.bat')), "run", "-n", "album", "album", "-h"],
                    capture_output=True)
                if cmd.returncode == 0:
                    if warned != 2:
                        album_version_check(yml_path=yml_path, conda=False, album=True, album_env_path=None,
                                            conda_path=conda_path)
                        if deleted:
                            return False

                    return True
                else:
                    return False
            else:
                cmd = subprocess.run(
                    [str(Path(conda_path).joinpath('condabin', 'conda')), "run", "-n", "album", "album", "-h"],
                    capture_output=True)
                if cmd.returncode == 0:
                    if warned != 2:
                        album_version_check(yml_path=yml_path, conda=False, album=True, album_env_path=None,
                                            conda_path=conda_path)
                        if deleted:
                            return False

                    return True
                else:
                    return False
        except Exception:
            return False


#    else:
#        return False


def check_for_script_installed_album(album_env_path, conda_path, yml_path):
    #    if not deleted:
    print("Script installed check")
    try:
        cmd = subprocess.run(["conda", "run", "-p", album_env_path, "album", "-h"], capture_output=True)
        if cmd.returncode == 0:
            if warned != 2:
                album_version_check(yml_path=yml_path, conda=True, album=False,
                                    album_env_path=album_env_path, conda_path=conda_path)
                if deleted:
                    return False
            return True
        else:
            return False
    except Exception:
        try:
            if platform.system() == 'Windows':
                cmd = subprocess.run(
                    [str(Path(conda_path).joinpath('condabin', 'conda.bat')), "run", "-p", album_env_path, "album",
                     "-h"], capture_output=True)
                if cmd.returncode == 0:
                    if warned != 2:
                        album_version_check(yml_path=yml_path, conda=False, album=False,
                                            album_env_path=album_env_path, conda_path=conda_path)
                        if deleted:
                            return False

                    return True
                else:
                    return False
            else:
                cmd = subprocess.run(
                    [str(Path(conda_path).joinpath('condabin', 'conda')), "run", "-p", album_env_path, "album", "-h"],
                    capture_output=True)
                if cmd.returncode == 0:
                    if warned != 2:
                        album_version_check(yml_path=yml_path, conda=False, album=False,
                                            album_env_path=album_env_path, conda_path=conda_path)
                        if deleted:
                            return False

                    return True
                else:
                    return False
        except Exception:
            return False


#    else:
#        return False


def check_for_preinstalled_gui(conda_path):
    # check if album gui is installed in the preinstalled album
    try:
        cmd = subprocess.run(["conda", "run", "-n", "album", "album", "gui", "-h"], capture_output=True)
        if cmd.returncode == 0:
            return True
        else:
            return False
    except Exception:
        try:
            if platform.system() == 'Windows':
                cmd = subprocess.run(
                    [str(Path(conda_path).joinpath('condabin', 'conda.exe')), "run", "-n", "album", "album", "gui",
                     "-h"], capture_output=True)
                # print("cmd2: %s" % cmd)
                if cmd.returncode == 0:
                    return True
                else:
                    return False
            else:
                cmd = subprocess.run(
                    [Path(conda_path).joinpath('condabin', 'conda'), "run", "-n", "album", "album", "gui", "-h"],
                    capture_output=True)
                if cmd.returncode == 0:
                    return True
                else:
                    return False
        except Exception:
            return False


def check_for_script_installed_gui(album_env_path, conda_path):
    # check if album gui is installed in the album installed via this script
    try:
        cmd = subprocess.run(["conda", "run", "-p", album_env_path, "album", "gui", "-h"], capture_output=True)
        if cmd.returncode == 0:
            return True
        else:
            return False
    except Exception:
        try:
            if platform.system() == 'Windows':
                cmd = subprocess.run(
                    [str(Path(conda_path).joinpath('condabin', 'conda.bat')), "run", "-p", album_env_path, "album",
                     "gui", "-h"], capture_output=True)
                if cmd.returncode == 0:
                    return True
                else:
                    return False
            else:
                cmd = subprocess.run(
                    [str(Path(conda_path).joinpath('condabin', 'conda')), "run", "-p", album_env_path, "album", "gui",
                     "-h"], capture_output=True)
                if cmd.returncode == 0:
                    return True
                else:
                    return False
        except Exception:
            return False


def check_for_preinstalled_conda():
    try:
        cmd = subprocess.run(["conda", "info"], capture_output=True)
        return True
    except Exception:
        return False


def check_for_script_installed_conda(conda_path):
    if platform.system() == 'Windows':
        conda_exe = str(Path(conda_path).joinpath('condabin', 'conda.bat'))
    else:
        conda_exe = str(Path(conda_path).joinpath('condabin', 'conda'))

    return os.path.isfile(Path(conda_exe))


def check_for_script_installed_pyshortcuts(album_env_path, conda_path):
    # check if pyshortcuts is installed in the album installed via this script
    try:
        cmd = subprocess.run(["conda", "run", "-p", album_env_path, "pyshortcut", "-h"], capture_output=True)
        if cmd.returncode == 0:
            return True
        else:
            return False
    except Exception:
        try:
            if platform.system() == 'Windows':
                cmd = subprocess.run(
                    [str(Path(conda_path).joinpath('condabin', 'conda.bat')), "run", "-p", album_env_path, "pyshortcut",
                     "-h"], capture_output=True)
                if cmd.returncode == 0:
                    return True
                else:
                    return False
            else:
                cmd = subprocess.run(
                    [str(Path(conda_path).joinpath('condabin', 'conda')), "run", "-p", album_env_path, "pyshortcut",
                     "-h"], capture_output=True)
                if cmd.returncode == 0:
                    return True
                else:
                    return False
        except Exception:
            return False


def check_for_preinstalled_pyshortcuts(conda_path):
    # check if album gui is installed in the preinstalled album
    try:
        cmd = subprocess.run(["conda", "run", "-n", "album", "pyshortcut", "-h"], capture_output=True)
        if cmd.returncode == 0:
            return True
        else:
            return False
    except Exception:
        try:
            if platform.system() == 'Windows':
                cmd = subprocess.run(
                    [str(Path(conda_path).joinpath('condabin', 'conda.exe')), "run", "-n", "album", "pyshortcut", "-h"],
                    capture_output=True)
                # print("cmd2: %s" % cmd)
                if cmd.returncode == 0:
                    return True
                else:
                    return False
            else:
                cmd = subprocess.run(
                    [Path(conda_path).joinpath('condabin', 'conda'), "run", "-n", "album", "pyshortcut", "-h"],
                    capture_output=True)
                if cmd.returncode == 0:
                    return True
                else:
                    return False
        except Exception:
            return False


def copy_icons(album_base_path):
    # copy the shortcut icons into album base if needed
    if not os.path.isdir(Path(album_base_path).joinpath('Solution_shortcuts')):
        if not os.path.isdir(album_base_path):
            os.mkdir(album_base_path)
        os.mkdir(Path(album_base_path).joinpath('Solution_shortcuts'))

    if (platform.system() == 'Windows') and (
            not os.path.isfile(Path(album_base_path).joinpath('Solution_shortcuts', 'album_icon_windows.ico'))):
        icon_path = str(Path(os.path.realpath(__file__)).parent.joinpath('album_icon_windows.ico'))
        shutil.copy(icon_path, Path(album_base_path).joinpath('Solution_shortcuts', 'album_icon_windows.ico'))
    elif (platform.system() == 'Darwin') and (
            not os.path.isfile(Path(album_base_path).joinpath('Solution_shortcuts', 'album_icon_macos.icns'))):
        icon_path = str(Path(os.path.realpath(__file__)).parent.joinpath('album_icon_macos.icns'))
        shutil.copy(icon_path, Path(album_base_path).joinpath('Solution_shortcuts', 'album_icon_macos.icns'))
    elif (platform.system() == 'Linux') and (
            not os.path.isfile(Path(album_base_path).joinpath('Solution_shortcuts', 'album_icon_linux.png'))):
        icon_path = str(Path(os.path.realpath(__file__)).parent.joinpath('album_icon_linux.png'))
        shutil.copy(icon_path, Path(album_base_path).joinpath('Solution_shortcuts', 'album_icon_linux.png'))
    elif os.path.isfile(
            Path(album_base_path).joinpath('Solution_shortcuts', 'album_icon_windows.ico')) or os.path.isfile(
        Path(album_base_path).joinpath('Solution_shortcuts', 'album_icon_macos.icns')) or os.path.isfile(
        Path(album_base_path).joinpath('Solution_shortcuts', 'album_icon_linux.png')):
        pass
    else:
        print("Your OS is currently not supported")
        raise NotImplementedError


def album_version_check(yml_path, conda, album, album_env_path, conda_path):
    print("VERSION CHECK")
    with open(yml_path, 'r') as file:
        for line in file:
            if line.startswith('      - album'):
                exe_version = line.split('==')[1]
    if conda:
        if album:
            cmd = subprocess.run(["conda", "run", "-n", "album", "album", "-V"], capture_output=True)
            installed_version = cmd.stdout.decode()
        else:
            cmd = subprocess.run(["conda", "run", "-p", album_env_path, "album", "-V"], capture_output=True)
            installed_version = cmd.stdout.decode()
    else:
        if platform.system() == 'Windows':
            if album:
                cmd = subprocess.run(
                    [str(Path(conda_path).joinpath('condabin', 'conda.exe')), "run", "-n", "album", "album", "-V"],
                    capture_output=True)
                installed_version = cmd.stdout.decode()
            else:
                cmd = subprocess.run(
                    [str(Path(conda_path).joinpath('condabin', 'conda.exe')), "run", "-p", album_env_path, "album",
                     "-V"], capture_output=True)
                installed_version = cmd.stdout.decode()
        else:
            if album:
                cmd = subprocess.run(
                    [str(Path(conda_path).joinpath('condabin', 'conda')), "run", "-n", "album", "album", "-V"],
                    capture_output=True)
                installed_version = cmd.stdout.decode()
            else:
                cmd = subprocess.run(
                    [str(Path(conda_path).joinpath('condabin', 'conda')), "run", "-p", album_env_path, "album", "-V"],
                    capture_output=True)
                installed_version = cmd.stdout.decode()

    installed_version = re.sub('\s', '', installed_version)
    exe_version = re.sub('\s', '', exe_version)
    global warned
    global deleted
    if installed_version == exe_version:
        warned += 1
        deleted = False
        return True
    else:
        if not warned:
            print(
                "WARNING: The Version of the installed album (%s) differs from the album used to create this executable (%s)." % (
                    installed_version, exe_version))
            if installed_version == '' or int(installed_version.split('.')[1]) < 7 or (int(installed_version.split('.')[1]) == 7 and int(installed_version.split('.')[2]) < 1):
                print("Your version seems to be older than 0.7.1. If you want to run album gui and this executable you need to reinstall album.")
            answer = input(
                "Do you want to delete the outdated album environment and if needed install a new version of album? (y/n)")
            while (True):
                if answer == 'y' or answer == 'yes':
                    if conda:
                        if album:
                            cmd = subprocess.run(["conda", "env", "remove", "-n", "album"], capture_output=True)
                        else:
                            cmd = subprocess.run(["conda", "env", "remove", "-p", album_env_path], capture_output=True)
                            shutil.rmtree(album_env_path)
                    else:
                        if platform.system() == 'Windows':
                            if album:
                                cmd = subprocess.run(
                                    [str(Path(conda_path).joinpath('condabin', 'conda.exe')), "env", "remove", "-n",
                                     "album"], capture_output=True)
                            else:
                                cmd = subprocess.run(
                                    [str(Path(conda_path).joinpath('condabin', 'conda.exe')), "env", "remove", "-p",
                                     album_env_path], capture_output=True)
                                shutil.rmtree(album_env_path)
                        else:
                            if album:
                                cmd = subprocess.run(
                                    [str(Path(conda_path).joinpath('condabin', 'conda')), "env", "remove", "-n",
                                     "album"], capture_output=True)
                            else:
                                cmd = subprocess.run(
                                    [str(Path(conda_path).joinpath('condabin', 'conda')), "env", "remove", "-p",
                                     album_env_path], capture_output=True)
                                shutil.rmtree(album_env_path)
                    deleted = True
                    return False
                elif answer == 'n' or answer == 'no':
                    deleted = False
                    break
                else:
                    answer = input("Invalid choise please enter y/yes or n/no.")
            warned += 1
        return False


def main():
    enc = sys.getfilesystemencoding()
    album_base_path = Path.home().joinpath('.album')
    _conda_path = Path(album_base_path).joinpath("Miniconda")
    album_env_path = Path(album_base_path).joinpath('envs', 'album')
    album_env_path = str(album_env_path)
    album_gui_url = "https://gitlab.com/album-app/plugins/album-gui/-/archive/main/album-gui-main.zip"
    yml_url = "https://gitlab.com/album-app/album/-/raw/main/album.yml"
    yml_path = Path(os.path.realpath(__file__)).parent.joinpath('album.yml')
    yml_path = str(yml_path)
    global warned
    warned = False

    # check if yml file is present
    if not os.path.isfile(yml_path):
        print("Downloading album yml file...")
        yml_path = Path(album_base_path).joinpath('album.yml')
        wget.download(yml_url, Path(yml_path))

    # copy shortcut icons into album base path
    copy_icons(album_base_path)

    print("Checking for conda installation...")
    if (not check_for_preinstalled_conda()) and (not check_for_script_installed_conda(_conda_path)):
        _install_missing_conda(_conda_path, album_base_path)

    print("Checking for album installation...")
    if (not check_for_preinstalled_album(_conda_path, yml_path)) and (
            not check_for_script_installed_album(album_env_path, _conda_path, yml_path)):
        _install_album_full(album_base_path, _conda_path, album_env_path, album_gui_url, yml_path)

    if not deleted:
        print("Checking for album gui installation...")
        if (not check_for_preinstalled_gui(_conda_path)) and (
                not check_for_script_installed_gui(album_env_path, _conda_path)):
            _install_missing_gui(album_base_path, _conda_path, album_env_path, album_gui_url, yml_path)

        print("Checking for PyShortcuts installation...")
        if (not check_for_preinstalled_pyshortcuts(_conda_path)) and (
                not check_for_script_installed_pyshortcuts(album_env_path, _conda_path)):
            _install_pyshortcuts(album_base_path, album_env_path, _conda_path, album_gui_url, yml_path)


if __name__ == '__main__':
    main()
