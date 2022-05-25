import os
from pathlib import Path
import PyInstaller.__main__
import shutil
from album.api import Album
from album.runner.album_logging import get_active_logger
from album.executable import create_spec_file_gui, create_subscripts_gui
from album.gui.app import AlbumGUI
from album.core.controller.task_manager import TaskManager


def run(album_instance: Album, args):
    #task_manager = TaskManager()
    #gui = AlbumGUI(album_instance, task_manager)
    #solution = args.solution
    create_subscripts_gui.run(args.solution, args.output_path)
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

