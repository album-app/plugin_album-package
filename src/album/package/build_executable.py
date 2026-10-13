import logging
import os
import platform
import re
import shutil
from pathlib import Path

import PyInstaller.__main__
from importlib.resources import open_text, files

from album.api import Album
from album.runner.album_logging import get_active_logger
from album.package.install_all import force_remove

# remove all handlers from root logger. Necessary because PyInstaller changes root logger configuration.
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
    handler.close()

# Folder inside the executable which contains the bundled solution. On the target system install_all.py copies it to a
# persistent location and installs the solution from there.
SOLUTION_BUNDLE_DIR = 'solution'

# Name of the solution file inside a solution directory (e.g. inside a catalog, an extracted zip file or a DOI download)
SOLUTION_FILE_NAME = 'solution.py'


def fill_placeholder(output_path, solution_path, coordinates):
    """Fills the path (relative to the bundle directory of the executable) and the coordinates of the passed solution
    into a cache file which gets copied into the executable so the information is available in the executable without
    destroying pyinstallers import structure"""
    with open_text('album.package', 'solution_info.txt') as file:
        template_str = file.read()

    # make windowspaths readable by escaping backslashes
    tmp = re.sub(r"\\", r"\\\\", solution_path)

    template_str = re.sub("<solution_placeholder>", tmp, template_str)
    template_str = re.sub(r"\\", r"\\\\", template_str)
    with open(Path(output_path).joinpath('solution_info.txt'), 'w') as file:
        file.write(template_str)
        file.write("\n")
        file.write(coordinates)


def get_solution_files(solution, resolve_result):
    """Returns the absolute path of the solution files which get bundled into the executable. An existing solution
    directory or solution file is bundled as it is. Otherwise (e.g. group:name:version, a DOI or a URL) the solution
    resolved by album is used: if the resolved file is a solution.py (solution in a catalog, extracted zip file or DOI
    download), its directory gets bundled. Any other resolved file gets bundled as a single file, e.g. a solution file
    downloaded from a URL, which album stores as a temporary file next to all its other downloads."""
    if Path(solution).exists():
        return Path(solution).absolute()
    resolved_solution_file = Path(resolve_result.path())
    if resolved_solution_file.name == SOLUTION_FILE_NAME:
        return resolved_solution_file.parent.absolute()
    return resolved_solution_file.absolute()


def prepare_solution_bundle(solution_files, output_path):
    """Prepares the solution files for bundling them into the executable.
    Returns the path which gets added to the executable and the path of the solution inside the executable bundle
    (relative to the bundle directory, written into solution_info.txt). A solution directory gets copied into the build
    directory first, so the output path does not get bundled in case it lies inside the solution directory."""
    solution_files = Path(solution_files)
    if solution_files.is_file():
        return solution_files, '%s/%s' % (SOLUTION_BUNDLE_DIR, solution_files.name)

    output_path = Path(output_path).resolve()
    if output_path == solution_files.resolve():
        raise RuntimeError("The output path %s must not be the solution directory itself, please use a sub directory "
                           "or any other directory" % output_path)

    def ignore_output_path(directory, names):
        if Path(directory).resolve() != output_path.parent:
            return []
        return [name for name in names if Path(directory).joinpath(name).resolve() == output_path]

    staging_path = output_path.joinpath('build', 'solution_bundle')
    force_remove(staging_path)
    shutil.copytree(solution_files, staging_path, ignore=ignore_output_path)
    return staging_path, SOLUTION_BUNDLE_DIR


def create_pyinstaller_params(args, name_param, solution_bundle=None):
    """creates the parameter for the pyinstaller call. solution_bundle is the solution file or directory which gets
    bundled into the executable (SOLUTION_BUNDLE_DIR inside the executable)."""
    work_dir = Path(args.output_path).joinpath('build')
    workpath_param = '--workpath=%s' % str(work_dir)
    exe_path_param = '--distpath=%s' % str(args.output_path)
    spec_path = Path(args.output_path)
    spec_path_param = '--specpath=%s' % str(args.output_path)
    log_level_param = '--log-level=ERROR'
    script_path = str(files('album.package').joinpath('install_all.py'))
    install_mamba_script = files('album.package').joinpath('install_mamba.py')
    install_mamba_param = '--add-data=%s%s%s' % (install_mamba_script, os.pathsep, '.')
    # PyInstaller resolves relative data paths relative to the spec path, therefore the absolute path is needed
    solution_info_path = str(Path(args.output_path).absolute().joinpath('solution_info.txt'))
    solution_info_param = '--add-data=%s%s%s' % (solution_info_path, os.pathsep, '.')

    pyinstaller_params = [script_path, '--onefile', name_param, exe_path_param, install_mamba_param,
                          solution_info_param, workpath_param, spec_path_param, log_level_param]

    if solution_bundle is not None:
        pyinstaller_params.append('--add-data=%s%s%s' % (solution_bundle, os.pathsep, SOLUTION_BUNDLE_DIR))

    return pyinstaller_params


def clean_up(output_path, name):
    force_remove(Path(output_path).joinpath('build'))
    force_remove(Path(output_path).joinpath('solution_info.txt'))
    force_remove(Path(output_path).joinpath('%s.spec' % name))


def run(album_instance: Album, args):
    """Build an executable which installs Album and the solution (in case provided)."""
    try:
        name = ""
        solution_bundle = None
        Path(args.output_path).mkdir(parents=True, exist_ok=True)

        if args.solution is None:
            get_active_logger().info("Build an executable which installs album.")
        if args.solution is not None:
            get_active_logger().info("Build an executable which installs the solution.")
            # args.solution is either a path to a solution file / directory or the coordinates of a solution
            resolve_result = album_instance.resolve(str(args.solution))
            coordinates = resolve_result.coordinates()
            if coordinates is None:
                raise RuntimeError("The provided solution %s does not contain valid coordinates." % args.solution)
            solution_files = get_solution_files(args.solution, resolve_result)
            get_active_logger().info(
                "solution: %s at %s" % (coordinates, solution_files))
            if platform.system() == "Darwin":
                name = "%s_%s_%s_installer.app" % (coordinates.group(), coordinates.name(),
                                                   str(coordinates.version()).replace('.', '_'))
                name_param = "--name=%s_%s_%s_installer.app" % (
                    coordinates.group(), coordinates.name(), str(coordinates.version()).replace('.', '_'))
            else:
                name = "%s_%s_%s_installer" % (coordinates.group(), coordinates.name(),
                                               str(coordinates.version()).replace('.', '_'))
                name_param = "--name=%s_%s_%s_installer" % (
                    coordinates.group(), coordinates.name(), str(coordinates.version()).replace('.', '_'))
            solution_bundle, bundled_solution = prepare_solution_bundle(solution_files, args.output_path)
            fill_placeholder(str(args.output_path), bundled_solution, coordinates.__str__())
        else:
            if platform.system() == "Darwin":
                name = "album_installer.app"
                name_param = "--name=album_installer.app"
            else:
                name = "album_installer"
                name_param = "--name=album_installer"
            fill_placeholder(str(args.output_path), str(args.solution), "None")

        get_active_logger().info("--output_path: %s" % args.output_path)

        pyinstaller_params = create_pyinstaller_params(args, name_param, solution_bundle)

    except Exception as e:
        clean_up(args.output_path, name)
        raise RuntimeError("Unexpected Error when preparing the executable build %s." % e) from e

    try:
        PyInstaller.__main__.run(pyinstaller_params)
    except Exception as e:
        raise RuntimeError("PyInstaller exited with an unexpected error! %s" % e) from e
    finally:
        clean_up(args.output_path, name)


