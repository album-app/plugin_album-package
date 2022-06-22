import os
import platform
import subprocess
import sys
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
    # exeption if conda is missing
    try:
        # check if there is an env present with the name album containing album gui and a conda installation with path env var
        cmd = subprocess.run(["conda", "run", "-n", "album", "album", "gui", "-h"], capture_output=True)
        # returncode != 0 if something is not right with album
        if cmd.returncode == 0:
            print("1%s" % cmd.returncode)
            install_return = call_named_album_install_conda_path()

            call_return = call_named_album_gui_conda_path()

            # 0 == everything went fine; 1 == solution was already installed
            if install_return != 0 and install_return != 1:
                sys.exit("There was an error installing the solution!")
            if call_return != 0:
                sys.exit("There was an error running the solution!")


        else:
            cmd = subprocess.run(
                ["conda", "run", "-p", Path.home().joinpath('.album', 'envs', 'album'), "album", "gui", "-h"],
                capture_output=True)
            print("2%s" % cmd.returncode)
            if cmd.returncode == 0:
                install_return = call_prefixed_album_install_conda_path()

                call_return = call_prefixed_album_gui_conda_path()

                # 0 == everything went fine; 1 == solution was already installed
                if install_return != 0 and install_return != 1:
                    sys.exit("There was an error installing the solution!")
                if call_return != 0:
                    sys.exit("There was an error running the solution!")

            else:
                print(
                    "Could not find album to run the solution. Please check your album installation.")

    except Exception as e:
        try:
            if platform.system() == 'Windows':
                # check if there is an env present with the name album containing album gui and a conda installation in the album base dir
                cmd = subprocess.run(
                    [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat'), "run", "-n", "album",
                     "album",
                     "-h"], capture_output=True)

                if cmd.returncode == 0:
                    print("3 %s" % cmd.returncode)
                    install_return = call_named_album_install_conda_exe()

                    call_return = call_named_album_gui_conda_exe()

                    # 0 == everything went fine; 1 == solution was already installed
                    if install_return != 0 and install_return != 1:
                        sys.exit("There was an error installing the solution!")
                    if call_return != 0:
                        sys.exit("There was an error running the solution!")

                else:
                    cmd = subprocess.run(
                        [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat'), "run", "-p",
                         Path.home().joinpath('.album', 'envs', 'album'), "album", "gui", "-h"],
                        capture_output=True)
                    print("4%s" % cmd.returncode)
                    if cmd.returncode == 0:
                        install_return = call_prefixed_album_install_conda_exe()

                        call_return = call_prefixed_album_gui_conda_exe()

                        # 0 == everything went fine; 1 == solution was already installed
                        if install_return != 0 and install_return != 1:
                            sys.exit("There was an error installing the solution!")
                        if call_return != 0:
                            sys.exit("There was an error running the solution!")

                    else:
                        print(
                            "Could not find album to run the solution. Please check your album installation.")

            else:
                # check if there is an env present with the name album containing album gui and a conda installation in the album base dir
                cmd = subprocess.run(
                    [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-n", "album",
                     "album",
                     "-h"], capture_output=True)

                if cmd.returncode == 0:
                    print("3 %s" % cmd.returncode)
                    install_return = call_named_album_install_conda_exe()

                    call_return = call_named_album_gui_conda_exe()

                    # 0 == everything went fine; 1 == solution was already installed
                    if install_return != 0 and install_return != 1:
                        sys.exit("There was an error installing the solution!")
                    if call_return != 0:
                        sys.exit("There was an error running the solution!")

                else:
                    cmd = subprocess.run(
                        [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-p",
                         Path.home().joinpath('.album', 'envs', 'album'), "album", "gui", "-h"],
                        capture_output=True)
                    print("4%s" % cmd.returncode)
                    if cmd.returncode == 0:
                        install_return = call_prefixed_album_install_conda_exe()

                        call_return = call_prefixed_album_gui_conda_exe()

                        # 0 == everything went fine; 1 == solution was already installed
                        if install_return != 0 and install_return != 1:
                            sys.exit("There was an error installing the solution!")
                        if call_return != 0:
                            sys.exit("There was an error running the solution!")

                    else:
                        print(
                            "Could not find album to run the solution. Please check your album installation.")

        except Exception:
            print(
                "An unexpected Error occured when runnig the solution. Please check your conda installation.")


if __name__ == "__main__":
    main()
