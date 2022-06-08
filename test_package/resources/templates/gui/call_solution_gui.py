import os
from pathlib import Path
import subprocess
from subprocess import check_output
import re
album_path = Path.home().joinpath('.album', 'env', 'album', 'Scripts','album.exe')
album_str = '%s'%album_path
conda_check = check_output('conda info')
conda_check = conda_check.decode()
conda_result = re.search('base environment : \S+',conda_check)
if conda_result:
	conda_path = re.split(': ',conda_result.group(0))[1]
	subprocess.call([Path(conda_path).joinpath('_conda.exe'), "run", "-p", Path.home().joinpath('.album', 'env', 'album'), album_str, "gui", "--solution", Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')])
else:
	subprocess.call([Path.home().joinpath('miniconda3','_conda.exe'), "run", "-p", Path.home().parent.joinpath('.album', 'env', 'album'), album_str, "gui", "--solution", Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')])
