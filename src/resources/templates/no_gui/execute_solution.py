import os
from pathlib import Path
import subprocess

python_path = Path(os.path.expanduser('~')).joinpath('.album', 'env', 'album', 'python.exe')
run_sol_path ='C:\\Users\\lriecke\\Desktop\\MDC\\Album\\plugins\\album-package\\src\\resources\\templates\\no_gui\\solution\\run_solution.py'
python_call = '%s %s' % (python_path, run_sol_path)
subprocess.call(python_call)
