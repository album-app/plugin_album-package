import os.path
import platform
import re
from pathlib import Path

import pkg_resources


def create(output_path, solution):
    ## create the spec file for pyinstaller for the no gui mode
    #spec_path = Path(output_path).joinpath('build_executable.spec')
    #yml_path = repr(str(Path(output_path).joinpath('album.yml')))
    #hook_path = repr(str(Path(pkg_resources.resource_filename('album.package.resources', 'install_all.py'))))
    #if os.path.isdir(Path(solution)):
    #    solution_path = repr(str(Path(solution).joinpath('*')))
    #if os.path.isfile(Path(solution)):
    #    solution_path = repr(str(Path(solution)))
#
    #with open(pkg_resources.resource_filename('album.package.resources.templates.no_gui',
    #                                          'build_executable_template.spec'), 'r') as file:
    #    template_str = file.read()
#
    #tmp = re.sub(r"\\", r"\\\\", yml_path)
    #template_str = re.sub("<yml_path>", tmp, template_str)
    #tmp = re.sub(r"\\", r"\\\\", solution_path)
    #template_str = re.sub("<solution_path>", tmp, template_str)
    #tmp = re.sub(r"\\", r"\\\\", hook_path)
    #template_str = re.sub("<hook_path>", tmp, template_str)
#
    #with open(spec_path, 'w') as file:
    #    file.write(template_str)
#
    #return spec_path

    # create the spec file for pyinstaller for the no gui mode
    spec_path = Path(output_path).joinpath('build_executable.spec')
    yml_path = repr(str(Path(output_path).joinpath('album.yml')))
    hook_path = repr(str(Path(pkg_resources.resource_filename('album.package.resources', 'install_all.py'))))
    run_sol_path = repr(
        str(pkg_resources.resource_filename('album.package.resources.templates.no_gui', 'run_solution.template')))
    uninstall_sol_path = repr(
        str(pkg_resources.resource_filename('album.package.resources.templates.no_gui', 'uninstall_solution.template')))

    if platform.system() == 'Windows':
        icon_path = repr(str(pkg_resources.resource_filename('album.package.resources', 'album_icon_windows.ico')))
    elif platform.system() == 'Darwin':
        icon_path = repr(str(pkg_resources.resource_filename('album.package.resources', 'album_icon_macos.icns')))
    elif platform.system() == 'Linux':
        icon_path = repr(str(pkg_resources.resource_filename('album.package.resources', 'album_icon_linux.png')))
    else:
        print("Your OS is currently not supported")
        raise NotImplementedError


    if os.path.isdir(Path(solution)):
        solution_path = repr(str(Path(solution).joinpath('*')))
    if os.path.isfile(Path(solution)):
        solution_path = repr(str(Path(solution)))

    with open(pkg_resources.resource_filename('album.package.resources.templates.no_gui',
                                              'build_executable_template_new.spec'), 'r') as file:
        template_str = file.read()

    tmp = re.sub(r"\\", r"\\\\", yml_path)
    template_str = re.sub("<yml_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", solution_path)
    template_str = re.sub("<solution_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", hook_path)
    template_str = re.sub("<hook_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", run_sol_path)
    template_str = re.sub("<run_sol_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", uninstall_sol_path)
    template_str = re.sub("<uninstall_sol_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", icon_path)
    template_str = re.sub("<icon>", tmp, template_str)

    with open(spec_path, 'w') as file:
        file.write(template_str)

    return spec_path
