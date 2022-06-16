import os
import platform
from pathlib import Path
import subprocess
from subprocess import check_output
try:
	conda_check = check_output('conda info')
	subprocess.call(["conda", "run", "-p", Path.home().joinpath('.album', 'envs', 'album'), "album", "install", Path(os.path.realpath(__file__)).parent.joinpath('solution_files')])
	subprocess.call(["conda", "run", "-p", Path.home().joinpath('.album', 'envs', 'album'), "album", "gui", "--solution", Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')])
except Exception as e:
	if platform.system() == 'Windows':
		subprocess.call([Path.home().joinpath('.album','Miniconda','condabin','conda.bat'), "run", "-p", Path.home().joinpath('.album', 'envs', 'album'), "album", "install", Path(os.path.realpath(__file__)).parent.joinpath('solution_files')])
		subprocess.call([Path.home().joinpath('.album','Miniconda','condabin','conda.bat'), "run", "-p", Path.home().joinpath('.album', 'envs', 'album'), "album", "gui", "--solution", Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')])
	else:
		subprocess.call([Path.home().joinpath('.album','Miniconda','condabin','conda'), "run", "-p", Path.home().joinpath('.album', 'envs', 'album'), "album", "install", Path(os.path.realpath(__file__)).parent.joinpath('solution_files')])
		subprocess.call([Path.home().joinpath('.album','Miniconda','condabin','conda'), "run", "-p", Path.home().joinpath('.album', 'envs', 'album'), "album", "gui", "--solution", Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')])
