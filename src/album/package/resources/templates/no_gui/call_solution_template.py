import os
import platform
import re
from pathlib import Path
import subprocess
import shutil

#commands = input('Please enter the parameters with which the package solution should be called:')
#commands = re.split(r'\s', commands)
params = ''
#for p in commands:
#    params += ' %s' %p

try:
    conda_check = subprocess.check_output('conda info')
    cmd = subprocess.run(["conda", "run", "-n", "album", "album", "index"])
    if cmd.returncode == 0:
        subprocess.run(["conda", "run", "-n", 'album', "album", "install",
                         Path(os.path.realpath(__file__)).parent.joinpath('solution_files')])
        subprocess.run(["conda", "run", "-n", 'album', "album", "run",
                         Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py'), params])
    else:
        subprocess.run(["conda", "run", "-p", Path.home().joinpath('.album', 'envs', 'album'), "album", "install",
                         Path(os.path.realpath(__file__)).parent.joinpath('solution_files')])
        subprocess.run(
            ["conda", "run", "-p", Path.home().joinpath('.album', 'envs', 'album'), "album", "run",
             Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py'), params])
except Exception as e:
    if platform.system() == 'Windows':
        cmd = subprocess.run(
            [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat'), "run", "-n", "album", "album",
             "index"])
        if cmd.returncode == 0:
            subprocess.run(
                [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat'), "run", "-n", 'album', "album",
                 "install", Path(os.path.realpath(__file__)).parent.joinpath('solution_files')])
            subprocess.run(
                [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat'), "run", "-n", 'album', "album",
                 "run", Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py'), params])
        else:
            subprocess.run([Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat'), "run", "-p",
                             Path.home().joinpath('.album', 'envs', 'album'), "album", "install",
                             Path(os.path.realpath(__file__)).parent.joinpath('solution_files')])
            subprocess.run([Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat'), "run", "-p",
                             Path.home().joinpath('.album', 'envs', 'album'), "album", "run",
                             Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py'), params])
    else:
        cmd = subprocess.run(
            [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-n", "album", "album",
             "index"])
        if cmd.returncode == 0:
            subprocess.run(
                [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-n", 'album', "album",
                 "install", Path(os.path.realpath(__file__)).parent.joinpath('solution_files')])
            subprocess.run(
                [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-n", 'album', "album", "run",
                 Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py'), params])
        else:
            subprocess.run([Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-p",
                             Path.home().joinpath('.album', 'envs', 'album'), "album", "install",
                             Path(os.path.realpath(__file__)).parent.joinpath('solution_files')])
            subprocess.run([Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-p",
                             Path.home().joinpath('.album', 'envs', 'album'), "album", "run",
                             Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py'), params])


