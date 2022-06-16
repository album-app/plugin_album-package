from album.api import Album
import os
import re
from pathlib import Path

sol_dir = Path(os.path.realpath(__file__)).parent.parent.joinpath('solution_files')
album = Album.Builder().base_cache_path("<base_path>").build()
album.load_or_create_collection()
if not album.is_installed(sol_dir):
    album.install(sol_dir)
commands = input('Please enter the parameters with which the package solution should be called:')
commands = re.split(r'\s', commands)
params = ['']
for p in commands:
    params.append(p)
album.run('<solution>', params)
