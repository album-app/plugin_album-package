import logging
import os
import re
import shutil
from pathlib import Path

import PyInstaller.__main__
import pkg_resources

from album.api import Album
from album.runner.album_logging import get_active_logger


# remove all handlers from root logger. Necessary because PyInstaller changes root logger configuration.
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
    handler.close()


def fill_placeholder(output_path, solution):
    with open(pkg_resources.resource_filename('album.package', 'solution_info.py'), 'r') as file:
        template_str = file.read()
    template_str = re.sub("<solution_placeholder>", solution, template_str)
    with open(Path(output_path).joinpath('solution_info.py'), 'w') as file:
        file.write(template_str)


def run(album_instance: Album, args):
    try:
        if (args.solution is not None) and (not (Path(args.solution).exists())):
            args.solution = album_instance.resolve(str(args.solution)).path()
        if args.solution is not None:
            coordinates = album_instance.resolve(str(args.solution)).coordinates()
            get_active_logger().info(
                "solution: %s at %s" % (coordinates, args.solution))
        get_active_logger().info("Build an executable which installs the solution.")
        get_active_logger().info("--output_path: %s" % args.output_path)

        if not Path(args.output_path).is_dir():
            Path(args.output_path).mkdir()

        fill_placeholder(str(args.output_path), str(args.solution))

        if args.solution is not None:
            name = "album_%s_installer" % "test"
            name_param = "--name=album_%s_installer" % "test"  #  coordinates
        else:
            name = "album_installer"
            name_param = "--name=album_installer"

        work_dir = Path(args.output_path).joinpath('build')
        exe_path_param = '--distpath=%s' % str(args.output_path)
        script_path = str(pkg_resources.resource_filename('album.package', 'install_all.py'))
        install_conda_script = pkg_resources.resource_filename('album.package', 'install_conda.py')
        install_conda_param = '--add-data=%s%s%s' % (install_conda_script, os.pathsep, '.')
        solution_info_path = str(Path(args.output_path).joinpath('solution_info.py'))
        solution_info_param = '--add-data=%s%s%s' % (solution_info_path, os.pathsep, '.')

        pyinstaller_params = [script_path, '--onefile', name_param, exe_path_param]
        pyinstaller_params.append(install_conda_param)
        pyinstaller_params.append(solution_info_param)

        hidden_imports = ["pkg_resources"]
        for hidden_import in hidden_imports:
            pyinstaller_params.append("--hidden-import=%s" % hidden_import)

        try:
            PyInstaller.__main__.run(pyinstaller_params)
        except Exception as e:
            raise RuntimeError("PyInstaller exited with an unexpected error! %s" % e) from e
        finally:
            if Path(work_dir).is_dir():
                shutil.rmtree(work_dir)
            Path(args.output_path).joinpath('solution_info.py').unlink()
            #Path(args.output_path).joinpath('%s.spec' % name).unlink()

    except Exception as e:
        get_active_logger().error("Unexpected Error when preparing the execution build %s." %e)
        #get_active_logger().error("album command failed: Cannot find solution %s! " \
        #                          "Try <doi>:<prefix>/<suffix> or <prefix>/<suffix> or <group>:<name>:<version> or " \
        #                          "<catalog>:<group>:<name>:<version> or point to a valid file! Aborting..." % (
        #                              args.solution))
