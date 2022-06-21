import os
import platform
import subprocess
from pathlib import Path


def call_named_album_install_conda_path():
    cmd = subprocess.run(["conda", "run", "-n", 'album', "album", "install",
                          Path(os.path.realpath(__file__)).parent.joinpath('solution_files')], capture_output=True)
    return cmd.returncode


def call_prefixed_album_install_conda_path():
    cmd = subprocess.run(["conda", "run", "-p", Path.home().joinpath('.album', 'envs', 'album'), "album", "install",
                          Path(os.path.realpath(__file__)).parent.joinpath('solution_files')], capture_output=True)
    return cmd.returncode


def call_named_album_install_conda_exe():
    if platform.system() == 'Windows':
        cmd = subprocess.run(
            [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat'), "run", "-n", 'album', "album",
             "install", Path(os.path.realpath(__file__)).parent.joinpath('solution_files')], capture_output=True)
        return cmd.returncode
    else:
        cmd = subprocess.run(
            [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-n", 'album', "album",
             "install", Path(os.path.realpath(__file__)).parent.joinpath('solution_files')], capture_output=True)
        return cmd.returncode


def call_prefixed_album_install_conda_exe():
    if platform.system() == 'Windows':
        cmd = subprocess.run([Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat'), "run", "-p",
                              Path.home().joinpath('.album', 'envs', 'album'), "album", "install",
                              Path(os.path.realpath(__file__)).parent.joinpath('solution_files')], capture_output=True)
        return cmd.returncode
    else:
        cmd = subprocess.run([Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-p",
                              Path.home().joinpath('.album', 'envs', 'album'), "album", "install",
                              Path(os.path.realpath(__file__)).parent.joinpath('solution_files')], capture_output=True)
        return cmd.returncode


def call_named_album_gui_conda_path():
    cmd = subprocess.run(["conda", "run", "-n", 'album', "album", "gui", "--solution",
                          Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')])
    return cmd.returncode


def call_prefixed_album_gui_conda_path():
    cmd = subprocess.run(
        ["conda", "run", "-p", Path.home().joinpath('.album', 'envs', 'album'), "album", "gui", "--solution",
         Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')])
    return cmd.returncode


def call_named_album_gui_conda_exe():
    if platform.system() == 'Windows':
        cmd = subprocess.run(
            [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat'), "run", "-n", 'album', "album", "gui",
             "--solution", Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')])
        return cmd.returncode
    else:
        cmd = subprocess.run(
            [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-n", 'album', "album", "gui",
             "--solution", Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')])
        return cmd.returncode


def call_prefixed_album_gui_conda_exe():
    if platform.system() == 'Windows':
        cmd = subprocess.run([Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat'), "run", "-p",
                              Path.home().joinpath('.album', 'envs', 'album'), "album", "gui", "--solution",
                              Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')])

        return cmd.returncode
    else:
        cmd = subprocess.run([Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-p",
                              Path.home().joinpath('.album', 'envs', 'album'), "album", "gui", "--solution",
                              Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')])

        return cmd.returncode


def main():
    try:
        # try conda with path var and named album env
        cmd = subprocess.run(["conda", "run", "-n", "album", "album", "-h"], capture_output=True)
        call_named_album_install_conda_path()
        call_named_album_gui_conda_path()

    except Exception as e:

        try:
            # try conda with path var and prefixed album env
            cmd = subprocess.run(["conda", "run", "-p", Path.home().joinpath('.album', 'envs', 'album'), "album", "-h"], capture_output=True)
            call_prefixed_album_install_conda_path()
            call_prefixed_album_gui_conda_path()
        except Exception:

            try:
                # try path to conda exe and named album env
                if platform.system() == 'Windows':
                    cmd = subprocess.run(
                        [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat'), "run", "-n", 'album',
                         "album",
                         "-h"],
                        capture_output=True)
                else:
                    cmd = subprocess.run(
                        [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-n", 'album',
                         "album",
                         "-h"], capture_output=True)
                call_named_album_install_conda_exe()
                call_named_album_gui_conda_exe()
            except Exception:
                # path to conda exe and prefixed album env
                try:
                    call_prefixed_album_install_conda_exe()
                    call_prefixed_album_gui_conda_exe()
                except Exception:
                    print(
                        "An unexpected Error occured when runnig the solution. Please check your conda and album installations.")


if __name__ == "__main__":
    main()
