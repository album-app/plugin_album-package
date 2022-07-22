import platform
import subprocess
import sys
from pathlib import Path


def call_conda_run(conda, album, mode):

    if mode == 'gui -h':
        if conda:
            if album:
                cmd = subprocess.run(["conda", "run", "-n", "album", "album", "gui", "-h"], capture_output=True)
                return cmd.returncode
            else:
                cmd = subprocess.run(["conda", "run", "-p", str(Path.home().joinpath('.album', 'envs', 'album')),
                                      "album", "gui", "-h"], capture_output=True)
                return cmd.returncode
        else:
            if album:
                if platform.system() == 'Windows':
                    cmd = subprocess.run(
                        [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-n",
                         "album", "album", "gui", "-h"], capture_output=True)
                    return cmd.returncode
                else:
                    cmd = subprocess.run(
                        [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda')), "run", "-n",
                         "album", "album", "gui", "-h"], capture_output=True)
                    return cmd.returncode
            else:
                if platform.system() == 'Windows':
                    cmd = subprocess.run(
                        [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-p",
                         str(Path.home().joinpath('.album', 'envs', 'album')), "album", "gui", "-h"],
                        capture_output=True)
                    return cmd.returncode
                else:
                    cmd = subprocess.run(
                        [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda')), "run", "-p",
                         str(Path.home().joinpath('.album', 'envs', 'album')), "album", "gui", "-h"],
                        capture_output=True)
                    return cmd.returncode

    elif mode == 'gui':
        run_input = '<solution>'
        if conda:
            if album:
                cmd = subprocess.run(["conda", "run", "-n", 'album', "album", "gui", "--solution", run_input],
                                     capture_output=True)
                return cmd.returncode
            else:
                cmd = subprocess.run(["conda", "run", "-p", str(Path.home().joinpath('.album', 'envs', 'album')),
                                      "album", "gui", "--solution", run_input], capture_output=True)
                return cmd.returncode
        else:
            if album:
                if platform.system() == 'Windows':
                    cmd = subprocess.run(
                        [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-n",
                         "album", "album", "gui", "--solution", run_input], capture_output=True)
                    return cmd.returncode
                else:
                    cmd = subprocess.run(
                        [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda')), "run", "-n",
                         "album", "album", "gui", "--solution", run_input], capture_output=True)
                    return cmd.returncode
            else:
                if platform.system() == 'Windows':
                    cmd = subprocess.run(
                        [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-p",
                         str(Path.home().joinpath('.album', 'envs', 'album')), "album", "gui", "--solution", run_input],
                        capture_output=True)
                    return cmd.returncode
                else:
                    cmd = subprocess.run(
                        [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda')), "run", "-p",
                         str(Path.home().joinpath('.album', 'envs', 'album')), "album", "gui", "--solution", run_input],
                        capture_output=True)
                    return cmd.returncode


def run_conda_path():
    # check if there is an env present with the name album containing album gui and a conda installation
    # with path env var
    returncode = call_conda_run(conda=True, album=True, mode='gui -h')
    if returncode == 0:
        call_return = call_conda_run(conda=True, album=True, mode='gui')
        if call_return != 0:
            sys.exit("There was an error running the solution!")
    else:
        # check if there is an env present with the script installed prefix containing album gui and a conda
        # installation with path env var
        returncode = call_conda_run(conda=True, album=False, mode='gui -h')
        if returncode == 0:
            call_return = call_conda_run(conda=True, album=False, mode='gui')
            if call_return != 0:
                sys.exit("There was an error running the solution!")
        else:
            sys.exit(
                "Could not find album to run the solution. Please check your album installation.")


def run_conda_exe():
    # check if there is an env present with the name album containing album gui and a conda installed with the
    # install script
    returncode = call_conda_run(conda=False, album=True, mode='gui -h')
    if returncode == 0:
        call_return = call_conda_run(conda=False, album=True, mode='gui')
        if call_return != 0:
            sys.exit("There was an error running the solution!")
    else:
        returncode = call_conda_run(conda=False, album=False, mode='gui -h')
        if returncode == 0:
            call_return = call_conda_run(conda=False, album=False, mode='gui')
            if call_return != 0:
                sys.exit("There was an error running the solution!")
        else:
            sys.exit(
                "Could not find album to run the solution. Please check your album installation.")


def main():
    try:
        run_conda_path()
    except Exception:
        try:
            run_conda_exe()
        except Exception as e:
            sys.exit(
                "An unexpected Error occurred when runnig the solution. Please check your conda installation. %s" % e)


if __name__ == "__main__":
    main()
