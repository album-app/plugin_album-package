import os

from album.api import Album
from album.executable import build_no_gui, build_gui
from album.runner.album_logging import get_active_logger


# -*- mode: python ; coding: utf-8 -*-


# Diese run startet nur eine spezifische run einer anderen datei wie z.b. create_spec, create_run_sol_script, create_hooks, create execution_script
# anhand der unterschiedlichen argumente der solution
def run(album_instance: Album, args):
    if os.path.isfile(args.solution):
        get_active_logger().info("Build an executable which runs the solution.")
        get_active_logger().info("--data_path: %s" % args.data_path)
        get_active_logger().info("--output_path: %s" % args.output_path)
        get_active_logger().info("--no_gui: %s" % args.no_gui)
        resolved_solution = album_instance.resolve(args.solution)
        get_active_logger().info("Resolved solution: %s" % resolved_solution.coordinates())

        mode = args.no_gui
        if not mode:
            print("BUILDING WITH GUI!!!!!!!!!!!")
            build_gui.run(album_instance, args)
            # raise NotImplementedError
        else:
            print("BUILDING NO GUI!!!!!!!!!!!")
            build_no_gui.run(album_instance, args)
    else:
        get_active_logger().error("Solution could not be found! Abort.")