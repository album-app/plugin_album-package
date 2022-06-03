import os
from pathlib import Path
import subprocess
if not (os.path.isdir(Path.home().joinpath('.album','env'))):
	print("Album missing, installing album.....")
	subprocess.call([Path(os.path.realpath(__file__)).parent.joinpath('install_album_win64.bat')])
else:
	print("Found Album. Proceeding to run the solution.")
