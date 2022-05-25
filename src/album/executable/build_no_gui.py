import os

from album.api import Album
from album.runner.album_logging import get_active_logger
from album.executable import create_spec_file_no_gui, create_subscripts_no_gui
from pathlib import Path
import PyInstaller.__main__
import shutil



def run(album_instance: Album, args):
    #calls an create_specfile und create_subscripts
    resolved_solution = album_instance.resolve(args.solution)
    solution_coordinates = resolved_solution.coordinates()
    create_subscripts_no_gui.run(args.solution,args.output_path,solution_coordinates)
    spec_path = create_spec_file_no_gui.run(args.output_path,args.solution)
    spec_path = str(spec_path)
    exe_path_param = '--distpath=%s' %(str(args.output_path))
    PyInstaller.__main__.run([spec_path,exe_path_param])

    #Deletion of PyInstaller leftovers
    if Path(os.getcwd()).joinpath('build', 'build_executable').exists():
        shutil.rmtree(Path(os.getcwd()).joinpath('build'))
    os.remove(Path(args.output_path).joinpath('build_executable.spec'))
    os.remove(Path(args.output_path).joinpath('execute_solution.py'))
    os.remove(Path(args.output_path).joinpath('install_hook.py'))
