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
        get_active_logger().info("Build an executable which runs the solution.")
        get_active_logger().info(
            "solution: %s at %s" % (album_instance.resolve(args.solution).coordinates(), args.solution))
        get_active_logger().info("--output_path: %s" % args.output_path)
        get_active_logger().info("--no_gui: %s" % args.no_gui)
        mode = args.no_gui
        if not mode:
            build_gui.run(args)
        else:
            build_no_gui.run(args)
    except AttributeError as e:
        get_active_logger().error("album command failed: Cannot find solution %s! " \
                    "Try <doi>:<prefix>/<suffix> or <prefix>/<suffix> or <group>:<name>:<version> or " \
                    "<catalog>:<group>:<name>:<version> or point to a valid file! Aborting... %s" %(args.solution,e))
