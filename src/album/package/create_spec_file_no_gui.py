import re
from pathlib import Path

import pkg_resources


def create(output_path, solution):
    spec_path = Path(output_path).joinpath('build_executable.spec')
    yml_path = repr(str(Path(output_path).joinpath('album.yml')))
    run_sol_path = repr(str(Path(output_path).joinpath('run_solution.py')))
    solution_path = repr(str(Path(solution).parent.joinpath('*.py')))
    hook_path = repr(str(Path(pkg_resources.resource_filename('album.package.resources', 'install_all.py'))))

    with open(pkg_resources.resource_filename('album.package.resources.templates.no_gui',
                                              'build_executable_template.spec'), 'r') as file:
        template_str = file.read()

    tmp = re.sub(r"\\", r"\\\\", yml_path)
    template_str = re.sub("<yml_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", run_sol_path)
    template_str = re.sub("<run_solution_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", solution_path)
    template_str = re.sub("<solution_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", hook_path)
    template_str = re.sub("<hook_path>", tmp, template_str)

    with open(spec_path, 'w') as file:
        file.write(template_str)

    return spec_path
