import os
import platform
import subprocess
import sys
from pathlib import Path

def call_named_album_gui_conda_path():
    # use a conda which can be called via conda command and a named album environment
    # to run the solution in the gui
    cmd = subprocess.run(["conda", "run", "-n", 'album', "album", "gui", "--solution", '<solution>'])
    return cmd.returncode


def call_prefixed_album_gui_conda_path():
    # use a conda which can be called via conda command and an album environment which got created with prefix and no
    # name to run the solution in the gui
    cmd = subprocess.run(
        ["conda", "run", "-p", str(Path.home().joinpath('.album', 'envs', 'album')), "album", "gui", "--solution",
         '<solution>'])
    return cmd.returncode


def call_named_album_gui_conda_exe():
    # use a conda which installed via the install script and a named album environment
    # to run the solution in the gui
    if platform.system() == 'Windows':
        cmd = subprocess.run(
            [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-n", 'album', "album", "gui",
             "--solution", '<solution>'])
        return cmd.returncode
    else:
        cmd = subprocess.run(
            [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-n", 'album', "album", "gui",
             "--solution", '<solution>'])
        return cmd.returncode


def call_prefixed_album_gui_conda_exe():
    # use a conda which was installed via the install script and an album environment which got created
    # with prefix and no name to run the solution in the gui
    if platform.system() == 'Windows':
        cmd = subprocess.run([str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-p",
                              str(Path.home().joinpath('.album', 'envs', 'album')), "album", "gui", "--solution",
                              '<solution>'])

        return cmd.returncode
    else:
        cmd = subprocess.run([Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-p",
                              Path.home().joinpath('.album', 'envs', 'album'), "album", "gui", "--solution",
                              '<solution>'])

        return cmd.returncode


try:
    # check if there is an env present with the name album containing album gui and a conda installation
    # with path env var
    cmd = subprocess.run(["conda", "run", "-n", "album", "album", "gui", "-h"], capture_output=True)
    # returncode != 0 if something is not right with album
    if cmd.returncode == 0:
        call_return = call_named_album_gui_conda_path()
        if call_return != 0:
            sys.exit("There was an error running the solution!")
    else:
        # check if there is an album env with prefix and a conda installation with path env var
        cmd = subprocess.run(
            ["conda", "run", "-p", str(Path.home().joinpath('.album', 'envs', 'album')), "album", "gui", "-h"],
            capture_output=True)
        #print("2%s" % cmd.returncode)
        if cmd.returncode == 0:
            call_return = call_prefixed_album_gui_conda_path()
            if call_return != 0:
                sys.exit("There was an error running the solution!")
        else:
            sys.exit(
                "Could not find album to run the solution. Please check your album installation.")

except Exception as e:
    try:
        if platform.system() == 'Windows':
            # check if there is an env present with the name album containing album gui and a conda installation
            # in the album base dir
            cmd = subprocess.run(
                [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-n", "album",
                 "album",
                 "-h"], capture_output=True)
            if cmd.returncode == 0:
                call_return = call_named_album_gui_conda_exe()
                if call_return != 0:
                    sys.exit("There was an error running the solution!")
            else:
                # check if there is an album env present with the install script prefix and
                # a conda installation in the album base dir
                cmd = subprocess.run(
                    [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-p",
                     str(Path.home().joinpath('.album', 'envs', 'album')), "album", "gui", "-h"],
                    capture_output=True)
                #print("4%s" % cmd.returncode)
                if cmd.returncode == 0:
                    call_return = call_prefixed_album_gui_conda_exe()
                    if call_return != 0:
                        sys.exit("There was an error running the solution!")
                else:
                    sys.exit(
                        "Could not find album to run the solution. Please check your album installation.")

        else:
            # check if there is an env present with the name album containing album gui and a conda installation
            # in the album base dir
            cmd = subprocess.run(
                [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-n", "album",
                 "album",
                 "-h"], capture_output=True)

            if cmd.returncode == 0:
                #print("3 %s" % cmd.returncode)
                call_return = call_named_album_gui_conda_exe()
                if call_return != 0:
                    sys.exit("There was an error running the solution!")
            else:
                # check if there is an album env present with the install script prefix and
                # a conda installation in the album base dir
                cmd = subprocess.run(
                    [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-p",
                     Path.home().joinpath('.album', 'envs', 'album'), "album", "gui", "-h"],
                    capture_output=True)
                #print("4%s" % cmd.returncode)
                if cmd.returncode == 0:
                    call_return = call_prefixed_album_gui_conda_exe()
                    if call_return != 0:
                        sys.exit("There was an error running the solution!")
                else:
                    sys.exit(
                        "Could not find album to run the solution. Please check your album installation.")

    except Exception:
        sys.exit(
            "An unexpected Error occured when runnig the solution. Please check your conda installation.")