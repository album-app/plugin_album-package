import os
from pathlib import Path
import subprocess
if not (os.path.isdir(Path.home().joinpath('.album', 'env'))) or not (os.path.isdir(Path.home().joinpath('.album', 'env', 'album', 'Lib', 'site-packages', 'album', 'gui'))):
	print("Album or Album Gui is missing, installing the missing component.....")
	subprocess.call([Path(os.path.realpath(__file__)).parent.joinpath('<install_script_path>')])
else:
	print("Found Album. Proceeding to run the solution.")
