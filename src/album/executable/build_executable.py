import os

from album.api import Album
from album.executable import build_no_gui, build_gui
from album.runner.album_logging import get_active_logger


# -*- mode: python ; coding: utf-8 -*-
#TODO: Das Powershell script in eine seperate Datei auslagern.

# starts the run fct corresponding to the selected gui mode
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
            build_gui.run(album_instance, args)
        else:
            build_no_gui.run(album_instance, args)
    else:
        get_active_logger().error("Solution could not be found! Abort.")