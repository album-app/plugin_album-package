import os
import shutil
from pathlib import Path

import PyInstaller.__main__

from album.api import Album
from album.package import create_spec_file_no_gui, create_subscripts_no_gui


def run(args, coordinates):
    # calls an create_specfile und create_subscripts
    if not os.path.isdir(Path(args.output_path)):
        os.mkdir(Path(args.output_path))

    create_subscripts_no_gui.create(args.output_path, coordinates)
    spec_path = create_spec_file_no_gui.create(args.output_path, args.solution)
    exe_path_param = '--noconsole, --distpath=%s' % (str(args.output_path))
    try:
        PyInstaller.__main__.run([str(spec_path), exe_path_param])
    except Exception as e:
        raise RuntimeError("PyInstaller exited with an unexpected error! %s" % e) from e
    finally:
        # Deletion of PyInstaller leftovers
        if Path(os.getcwd()).joinpath('build', 'build_executable').exists():
            shutil.rmtree(Path(os.getcwd()).joinpath('build'))
        os.remove(Path(args.output_path).joinpath('build_executable.spec'))
        os.remove(Path(args.output_path).joinpath('call_solution.py'))
        os.remove(Path(args.output_path).joinpath('album.yml'))
