import os
import platform
import re
import subprocess
from pathlib import Path


def call_named_album_install_conda_path():
    cmd = subprocess.run(["conda", "run", "-n", "album", "album", "install",
                          Path(os.path.realpath(__file__)).parent.joinpath('solution_files')], capture_output=True)
    return cmd.returncode


def call_named_album_run_conda_path(params):
    cmd = subprocess.run(["conda", "run", "-n", "album", "album", "run",
                          Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py'), params])
    return cmd.returncode


def call_prefixed_album_install_conda_path():
    cmd = subprocess.run(["conda", "run", "-p", Path.home().joinpath('.album', 'envs', 'album'), "album", "install",
                          Path(os.path.realpath(__file__)).parent.joinpath('solution_files')], capture_output=True)
    return cmd.returncode


def call_prefixed_album_run_conda_path(params):
    cmd = subprocess.run(
        ["conda", "run", "-p", Path.home().joinpath('.album', 'envs', 'album'), "album", "run",
         Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py'), params])
    return cmd.returncode


def call_named_album_install_conda_exe():
    if platform.system() == 'Windows':
        cmd = subprocess.run(
            [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat'), "run", "-n", "album", "album",
             "install", Path(os.path.realpath(__file__)).parent.joinpath('solution_files')], capture_output=True)
        return cmd.returncode
    else:
        cmd = subprocess.run(
            [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-n", "album", "album",
             "install", Path(os.path.realpath(__file__)).parent.joinpath('solution_files')], capture_output=True)
        return cmd.returncode


def call_named_album_run_conda_exe(params):
    if platform.system() == 'Windows':
        cmd = subprocess.run(
            [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat'), "run", "-n", "album", "album",
             "run", Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py'), params])
        return cmd.returncode
    else:
        cmd = subprocess.run(
            [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-n", "album", "album", "run",
             Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py'), params])
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


def call_prefixed_album_run_conda_exe(params):
    if platform.system() == 'Windows':
        cmd = subprocess.run([Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat'), "run", "-p",
                              Path.home().joinpath('.album', 'envs', 'album'), "album", "run",
                              Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py'),
                              params])
        return cmd.returncode
    else:
        cmd = subprocess.run([Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-p",
                              Path.home().joinpath('.album', 'envs', 'album'), "album", "run",
                              Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py'),
                              params])
        return cmd.returncode


def get_params():
    commands = input('Please enter the parameters with which the package solution should be called:')
    commands = re.split(r'\s', commands)
    params = ''
    for p in commands:
        params += ' %s' % p
    return params


def main():
    params = get_params()
    #exeption if conda is missing
    try:
        # check if there is an env present with the name album and a conda installation with path env var
        cmd = subprocess.run(["conda", "run", "-n", "album", "album", "-h"], capture_output=True)
        #returncode != 0 if something is not right with album
        if cmd.returncode == 0:
            print("1%s" %cmd.returncode)
            call_named_album_install_conda_path()

            call_named_album_run_conda_path(params)

        else:
            print("2%s" %cmd.returncode)
            call_prefixed_album_install_conda_path()

            call_prefixed_album_run_conda_path(params)

    except Exception as e:
        try:
            if platform.system() == 'Windows':
                # check if there is an env present with the name album and a conda installation in the album base dir
                cmd = subprocess.run(
                    [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat'), "run", "-n", "album",
                     "album",
                     "-h"], capture_output=True)

                if cmd.returncode == 0:
                    print("3 %s" % cmd.returncode)
                    call_named_album_install_conda_exe()

                    call_named_album_run_conda_exe(params)
                else:
                    print("4%s" % cmd.returncode)
                    call_prefixed_album_install_conda_exe()

                    call_prefixed_album_run_conda_exe(params)

            else:
                # check if there is an env present with the name album and a conda installation in the album base dir
                cmd = subprocess.run(
                    [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-n", "album",
                     "album",
                     "-h"], capture_output=True)

                if cmd.returncode == 0:
                    print("3 %s" % cmd.returncode)
                    call_named_album_install_conda_exe()

                    call_named_album_run_conda_exe(params)
                else:
                    print("4%s" % cmd.returncode)
                    call_prefixed_album_install_conda_exe()

                    call_prefixed_album_run_conda_exe(params)

        except Exception:
            print(
                "An unexpected Error occured when runnig the solution. Please check your conda and album installations.")


if __name__ == "__main__":
    main()
