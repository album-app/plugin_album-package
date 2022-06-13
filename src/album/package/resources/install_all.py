import os.path
import platform
import subprocess
from pathlib import Path
import wget


def _install_conda_windows(conda_path):
    conda_url_win = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
    conda_installer = Path(conda_path).joinpath("Miniconda_install.exe")
    wget.download(conda_url_win, str(conda_installer))
    cmd = "Start-Process %s -argumentlist \"/InstallationType=JustMe /S /D=%s\" -wait" % (
        conda_installer, conda_path)
    install_process = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    conda_exe = Path(conda_path).joinpath("_conda.exe")

    if install_process.returncode != 0:
        print("An error occured when installing Conda: %s", install_process.stderr)
    else:
        print("Successfully installed Miniconda.")

    return conda_exe


def _install_conda_linux(conda_path):
    conda_url_linux = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    conda_installer = Path(conda_path).joinpath("Miniconda_install.sh")
    wget.download(conda_url_linux, str(conda_installer))
    install_process = subprocess.run(["bash", conda_installer, "-b", "-u", "-p", conda_path, ">", "/dev/null"],
                                     capture_output=True)
    conda_exe = Path(conda_path).joinpath("_conda")

    if install_process.returncode != 0:
        print("An error occured when installing Conda: %s", install_process.stderr)
    else:
        print("Successfully installed Miniconda.")

    return conda_exe


def _install_conda_macos(conda_path):
    conda_url_macos = "https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
    conda_installer = Path(conda_path).joinpath("Miniconda_install.sh")
    wget.download(conda_url_macos, str(conda_installer))
    install_process = subprocess.run(["bash", conda_installer, "-b", "-u", "-p", conda_path, ">", "/dev/null"],
                                     capture_output=True)
    conda_exe = Path(conda_path).joinpath("_conda")

    if install_process.returncode != 0:
        print("An error occured when installing Conda: %s", install_process.stderr)
    else:
        print("Successfully installed Miniconda.")

    return conda_exe


def main():
    album_base_path = Path.home().joinpath('.album')
    _conda_path = Path(album_base_path).joinpath("Miniconda")
    album_env_path = Path(album_base_path).joinpath('envs', 'album')
    album_gui_url = "https://gitlab.com/album-app/plugins/album-gui/-/archive/main/album-gui-main.zip"


    if not (os.path.isdir(album_base_path)):
        print("Could not find album. Checking for conda installation....")
        os.mkdir(album_base_path)

        try:
            tmp = subprocess.check_output('conda info')
            print("Conda Command available.")
            conda_found = True

        except Exception as e:
            print("Conda command not available. Installing Miniconda into " + str(_conda_path))
            conda_found = False
            # if it is directory check if there is an working conda exe inside
            if not os.path.isdir(_conda_path):
                os.mkdir(_conda_path)

                if platform.system() == 'Windows':
                    conda_exe = _install_conda_windows(_conda_path)

                elif platform.system() == 'Linux':
                    conda_exe = _install_conda_linux(_conda_path)

                elif platform.system() == 'Darwin':
                    conda_exe = _install_conda_macos(_conda_path)

                else:
                    raise NotImplementedError

            print("-------------------------")

        print("Installing album...")
        yml_path = Path(os.path.realpath(__file__)).parent.joinpath('album.yml')
        if conda_found:
            subprocess.call('conda env create -p %s -f %s' % (album_env_path, yml_path))
            subprocess.call('conda run -p %s pip install %s ' % (album_env_path, album_gui_url))
        else:
            subprocess.call('%s env create -p %s -f %s' % (conda_exe, album_env_path, yml_path))
            subprocess.call('%s run -p %s pip install %s ' % (conda_exe, album_env_path, album_gui_url))


if __name__ == '__main__':
    main()
