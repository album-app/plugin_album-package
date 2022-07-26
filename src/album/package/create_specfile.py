import os.path
import platform
import re
from pathlib import Path

import pkg_resources


def create(output_path, solution):
    spec_path = Path(output_path).joinpath('build_executable.spec')
    yml_path = repr(str(Path(output_path).joinpath('album.yml')))
    hook_path = repr(str(Path(pkg_resources.resource_filename('album.package.resources.installer', 'install_all.py'))))
    call_sol_path = repr(str(Path(output_path).joinpath('call_solution.py')))
    run_sol_path = repr(
        str(pkg_resources.resource_filename('album.package.resources.templates', 'run_solution.template')))
    run_sol_gui_path = repr(
        str(pkg_resources.resource_filename('album.package.resources.templates',
                                            'run_solution_gui.template')))
    uninstall_sol_path = repr(
        str(pkg_resources.resource_filename('album.package.resources.templates',
                                            'uninstall_solution.template')))
    uninstall_sol_gui_path = repr(
        str(pkg_resources.resource_filename('album.package.resources.templates',
                                            'uninstall_solution_gui.template')))
    if platform.system() == 'Windows':
        icon_path = repr(str(pkg_resources.resource_filename('album.package.resources.icons', 'album_icon_windows.ico')))
        installer_path = repr(str(pkg_resources.resource_filename('album.package.resources.installer',
                                                                  'Miniconda_installer_windows.exe')))
    elif platform.system() == 'Darwin':
        icon_path = repr(str(pkg_resources.resource_filename('album.package.resources.icons', 'album_icon_macos.icns')))
        installer_path = repr(str(pkg_resources.resource_filename('album.package.resources.installer',
                                                                  'Miniconda_installer_macos.sh')))
    elif platform.system() == 'Linux':
        icon_path = repr(str(pkg_resources.resource_filename('album.package.resources.icons', 'album_icon_linux.png')))
        installer_path = repr(str(pkg_resources.resource_filename('album.package.resources.installer',
                                                                  'Miniconda_installer_linux.sh')))
    else:
        print("Your OS is currently not supported")
        raise NotImplementedError

    if os.path.isdir(Path(solution)):
        solution_path = repr(str(Path(solution).joinpath('*')))
    if os.path.isfile(Path(solution)):
        solution_path = repr(str(Path(solution)))

    with open(pkg_resources.resource_filename('album.package.resources.templates',
                                              'build_executable_spec.template'), 'r') as file:
        template_str = file.read()

    tmp = re.sub(r"\\", r"\\\\", yml_path)
    template_str = re.sub("<yml_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", solution_path)
    template_str = re.sub("<solution_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", hook_path)
    template_str = re.sub("<hook_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", run_sol_path)
    template_str = re.sub("<run_sol_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", run_sol_gui_path)
    template_str = re.sub("<run_sol_gui_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", uninstall_sol_path)
    template_str = re.sub("<uninstall_sol_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", uninstall_sol_gui_path)
    template_str = re.sub("<uninstall_sol_gui_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", icon_path)
    template_str = re.sub("<icon>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", call_sol_path)
    template_str = re.sub("<call_sol_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", installer_path)
    template_str = re.sub("<conda_installer>", tmp, template_str)

    with open(spec_path, 'w') as file:
        file.write(template_str)

    return spec_path
