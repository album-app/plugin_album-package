import os
import platform
import re
import subprocess
import sys
from pathlib import Path


def call_named_album_install_conda_path():
    # use a conda which can be called via conda command and an environment called album to install the solution
    cmd = subprocess.run(["conda", "run", "-n", "album", "album", "install",
                          str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files'))], capture_output=True)
    return cmd.returncode


def call_named_album_run_conda_path(params):
    # use a conda which can be called via conda command and an environment called album to run the solution
    cmd = subprocess.run(["conda", "run", "-n", "album", "album", "run",
                          str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')), params])
    return cmd.returncode


def call_prefixed_album_install_conda_path():
    # use a conda which can be called via conda command and an album environment which got created with prefix and no
    # name to install the solution
    cmd = subprocess.run(["conda", "run", "-p", str(Path.home().joinpath('.album', 'envs', 'album')), "album", "install",
                          str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files'))], capture_output=True)
    return cmd.returncode


def call_prefixed_album_run_conda_path(params):
    # use a conda which can be called via conda command and an album environment which got created with prefix and no
    # name to run the solution
    cmd = subprocess.run(
        ["conda", "run", "-p", str(Path.home().joinpath('.album', 'envs', 'album')), "album", "run",
         str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')), params])
    return cmd.returncode


def call_named_album_install_conda_exe():
    # use a conda which installed via the install script and an environment called album to install the solution
    if platform.system() == 'Windows':
        cmd = subprocess.run(
            [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-n", "album", "album",
             "install", str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files'))], capture_output=True)
        return cmd.returncode
    else:
        cmd = subprocess.run(
            [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-n", "album", "album",
             "install", Path(os.path.realpath(__file__)).parent.joinpath('solution_files')], capture_output=True)
        return cmd.returncode


def call_named_album_run_conda_exe(params):
    # use a conda which installed via the install script and an environment called album to run the solution
    if platform.system() == 'Windows':
        cmd = subprocess.run(
            [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-n", "album", "album",
             "run", str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')), params])
        return cmd.returncode
    else:
        cmd = subprocess.run(
            [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-n", "album", "album", "run",
             Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py'), params])
        return cmd.returncode


def call_prefixed_album_install_conda_exe():
    # use a conda which installed via the install script and an album environment which got created with prefix and no
    #     # name to install the solution
    if platform.system() == 'Windows':
        cmd = subprocess.run([str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-p",
                              str(Path.home().joinpath('.album', 'envs', 'album')), "album", "install",
                              str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files'))], capture_output=True)
        return cmd.returncode
    else:
        cmd = subprocess.run([Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-p",
                              Path.home().joinpath('.album', 'envs', 'album'), "album", "install",
                              Path(os.path.realpath(__file__)).parent.joinpath('solution_files')])
        print(cmd.returncode)
        return cmd.returncode


def call_prefixed_album_run_conda_exe(params):
    # use a conda which was installed via the install script and an album environment which got created with prefix and no
    # name to run the solution
    if platform.system() == 'Windows':
        cmd = subprocess.run([str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-p",
                              str(Path.home().joinpath('.album', 'envs', 'album')), "album", "run",
                              str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')),
                              params])
        return cmd.returncode
    else:
        cmd = subprocess.run([Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-p",
                              Path.home().joinpath('.album', 'envs', 'album'), "album", "run",
                              Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py'),
                              params])
        return cmd.returncode


def get_params():
    # get input parameter for the solution
    commands = input('Please enter the parameters with which the package solution should be called:')
    if isinstance(commands, bytes):
        commands = commands.decode()

    commands = re.split(r'\s', commands)
    params = ''
    for p in commands:
        params += ' %s' % p
    return params


def main():
    params = get_params()
    # exeption if conda is missing

    cmd = subprocess.run(["conda", "run", "-n", "album", "album", "-h"], capture_output=True)
    print("COMMAND!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! %s" %cmd)
    try:
        # check if there is an env present with the name album and a conda installation with path env var
        cmd = subprocess.run(["conda", "run", "-n", "album", "album", "-h"], capture_output=True)
        # returncode != 0 if something is not right with album
        if cmd.returncode == 0:
            print("1%s" % cmd.returncode)
            install_return = call_named_album_install_conda_path()

            call_return = call_named_album_run_conda_path(params)
            # 0 == everything went fine; 1 == solution was already installed
            #FIXME: returncode 1 is not unique for already installed solution, it stands for all sorts of errors, like solution not found
            if install_return != 0 and install_return != 1:
                sys.exit("There was an error installing the solution!")
            if call_return != 0:
                sys.exit("There was an error running the solution!")

        else:
            #check if there is an album env with prefix and a conda installation with path env var
            cmd = subprocess.run(["conda", "run", "-p", str(Path.home().joinpath('.album', 'envs', 'album')), "album", "-h"], capture_output=True)
            print("2! %s" % cmd.returncode)
            if cmd.returncode == 0:
                install_return = call_prefixed_album_install_conda_path()

                call_return = call_prefixed_album_run_conda_path(params)
                # 0 == everything went fine; 1 == solution was already installed
                if install_return != 0 and install_return != 1:
                    sys.exit("There was an error installing the solution!")
                if call_return != 0:
                    sys.exit("There was an error running the solution!")

            else:
                print(
                    "Could not find album to run the solution. Please check your album installation.")
    # TODO: try exception subprocess.CalledProcessError and run(check=True) as replacement for Exception
    except Exception as e:
        print("EXECEPTION!!!!!!!!!!!!!!!!!!!!!!!!!!!!! %s" % e)
        try:
            if platform.system() == 'Windows':
                # check if there is an env present with the name album and a conda installation in the album base dir
                cmd = subprocess.run(
                    [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-n", "album",
                     "album",
                     "-h"], capture_output=True)
                print("3 %s" % cmd.returncode)
                if cmd.returncode == 0:

                    install_return = call_named_album_install_conda_exe()

                    call_return = call_named_album_run_conda_exe(params)

                    # 0 == everything went fine; 1 == solution was already installed
                    if install_return != 0 and install_return != 1:
                        sys.exit("There was an error installing the solution!")
                    if call_return != 0:
                        sys.exit("There was an error running the solution!")

                else:
                    # check if there is an album env present with the install script prefix and
                    # a conda installation in the album base dir
                    cmd = subprocess.run(
                        [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-p",
                         str(Path.home().joinpath('.album', 'envs', 'album')), "album", "-h"],
                        capture_output=True)
                    print("4%s" % cmd.returncode)
                    if cmd.returncode == 0:
                        install_return = call_prefixed_album_install_conda_exe()

                        call_return = call_prefixed_album_run_conda_exe(params)

                        # 0 == everything went fine; 1 == solution was already installed
                        if install_return != 0 and install_return != 1:
                            sys.exit("There was an error installing the solution!")
                        if call_return != 0:
                            sys.exit("There was an error running the solution!")

                    else:
                        print(
                            "Could not find album to run the solution. Please check your album installation.")

            else:
                # check if there is an env present with the name album and a conda installation in the album base dir
                cmd = subprocess.run(
                    [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-n", "album",
                     "album",
                     "-h"], capture_output=True)

                if cmd.returncode == 0:
                    print("3 %s" % cmd.returncode)
                    install_return = call_named_album_install_conda_exe()

                    call_return = call_named_album_run_conda_exe(params)

                    # 0 == everything went fine; 1 == solution was already installed
                    if install_return != 0 and install_return != 1:
                        sys.exit("There was an error installing the solution!")
                    if call_return != 0:
                        sys.exit("There was an error running the solution!")

                else:
                    # check if there is an album env present with the install script prefix and
                    # a conda installation in the album base dir
                    cmd = subprocess.run(
                        [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-p",
                         Path.home().joinpath('.album', 'envs', 'album'), "album", "-h"],
                        capture_output=True)
                    print("4%s" % cmd.returncode)
                    print(cmd.stderr.decode())
                    if cmd.returncode == 0:
                        install_return = call_prefixed_album_install_conda_exe()

                        call_return = call_prefixed_album_run_conda_exe(params)

                        # 0 == everything went fine; 1 == solution was already installed
                        if install_return != 0 and install_return != 1:
                            sys.exit("There was an error installing the solution!")
                        if call_return != 0:
                            sys.exit("There was an error running the solution!")

                    else:
                        print(
                            "Could not find album to run the solution. Please check your album installation.")

        except Exception as e:
            print(
                "An unexpected Error occured when runnig the solution. Please check your conda installation: %s" % e)


if __name__ == "__main__":
    main()
