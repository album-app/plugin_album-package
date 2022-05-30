import os
import shutil
from pathlib import Path

import PyInstaller.__main__

from album.api import Album
from album.executable import create_spec_file_gui, create_subscripts_gui
from album.runner.album_logging import get_active_logger


def run(album_instance: Album, args):
    if not os.path.isdir(Path(args.output_path)):
        os.mkdir(Path(args.output_path))
    create_subscripts_gui.run(args.output_path)
    spec_path = create_spec_file_gui.run(args.output_path, args.solution)
    spec_path = str(spec_path)
    exe_path_param = '--distpath=%s' % (str(args.output_path))
    PyInstaller.__main__.run([spec_path, exe_path_param])

    # Deletion of PyInstaller leftovers
    if Path(os.getcwd()).joinpath('build', 'build_executable_gui').exists():
        shutil.rmtree(Path(os.getcwd()).joinpath('build'))
    os.remove(Path(args.output_path).joinpath('build_executable_gui.spec'))
    os.remove(Path(args.output_path).joinpath('execute_solution_gui.py'))
    os.remove(Path(args.output_path).joinpath('install_hook.py'))
