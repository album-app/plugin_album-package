import os
from pathlib import Path
import subprocess
import shutil

conda_path = shutil.which("conda")
env_path = Path.home().joinpath('.album', 'envs', 'album')
python_path = Path.home().joinpath('.album', 'envs', 'album', 'python')
run_sol_path = Path(os.path.realpath(__file__)).parent.joinpath('subscripts', 'run_solution.py')
python_call = '%s %s' % (python_path, run_sol_path)
subprocess.call(python_call)
input('Press any key to exit.')
