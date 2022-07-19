import logging
import os
import shutil
from pathlib import Path

from album.api import Album
#from album.package import create_subscripts, create_spec_file
from album.runner.album_logging import get_active_logger

import PyInstaller.__main__

# remove all handlers from root logger. Necessary because PyInstaller changes root logger configuration.
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
    handler.close()


#def run(album_instance: Album, args):
#    try:
#        if not (Path.exists(Path(args.solution))):
#            args.solution = album_instance.resolve(args.solution).path()
#        coordinates = album_instance.resolve(args.solution).coordinates()
#        get_active_logger().info("Build an executable which runs the solution.")
#        get_active_logger().info(
#            "solution: %s at %s" % (coordinates, args.solution))
#        get_active_logger().info("--output_path: %s" % args.output_path)
#        get_active_logger().info("--no_gui: %s" % args.no_gui)
#        mode = args.no_gui
#
#        if not os.path.isdir(Path(args.output_path)):
#            os.mkdir(Path(args.output_path))
#
#        create_subscripts.create(args.output_path, coordinates, mode)
#        spec_path = create_spec_file.create(args.output_path, args.solution, mode)
#        exe_path_param = '--distpath=%s' % (str(args.output_path))
#        try:
#            PyInstaller.__main__.run([str(spec_path), exe_path_param])
#        except Exception as e:
#            raise RuntimeError("PyInstaller exited with an unexpected error! %s" % e) from e
#        finally:
#            if Path(os.getcwd()).joinpath('build', 'build_executable').exists():
#                shutil.rmtree(Path(os.getcwd()).joinpath('build'))
#            os.remove(Path(args.output_path).joinpath('build_executable.spec'))
#            os.remove(Path(args.output_path).joinpath('call_solution.py'))
#            os.remove(Path(args.output_path).joinpath('album.yml'))
#
#    except AttributeError as e:
#        get_active_logger().error("album command failed: Cannot find solution %s! " \
#                    "Try <doi>:<prefix>/<suffix> or <prefix>/<suffix> or <group>:<name>:<version> or " \
#                    "<catalog>:<group>:<name>:<version> or point to a valid file! Aborting..." %(args.solution))


import os
from pathlib import Path

from album.api import Album
from album.package import build_no_gui, build_gui
from album.runner.album_logging import get_active_logger


# -*- mode: python ; coding: utf-8 -*-

# starts the run fct corresponding to the selected gui mode
def run(album_instance: Album, args):
    try:
        if not (Path.exists(Path(args.solution))):
            args.solution = album_instance.resolve(args.solution).path()
        coordinats = album_instance.resolve(args.solution).coordinates()
        get_active_logger().info("Build an executable which runs the solution.")
        get_active_logger().info(
            "solution: %s at %s" % (coordinats, args.solution))
        get_active_logger().info("--output_path: %s" % args.output_path)
        get_active_logger().info("--no_gui: %s" % args.no_gui)
        mode = args.no_gui

        if not mode:
            build_gui.run(args,coordinats)
        else:
            build_no_gui.run(args, coordinats)
    except AttributeError as e:
        get_active_logger().error("album command failed: Cannot find solution %s! " \
                    "Try <doi>:<prefix>/<suffix> or <prefix>/<suffix> or <group>:<name>:<version> or " \
                    "<catalog>:<group>:<name>:<version> or point to a valid file! Aborting..." %(args.solution))
