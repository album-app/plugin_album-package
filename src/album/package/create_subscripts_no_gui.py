import re
from pathlib import Path
from album import core

import pkg_resources


def create(output_path, solution_coordinates):
    create_yml(output_path)
    create_run_solution(output_path, solution_coordinates)
    create_call_solution(output_path)


def create_yml(output_path):
    yml_path = Path(output_path).joinpath('album.yml')
    with open(pkg_resources.resource_filename('album.package.resources.templates', 'album.yml'), 'r') as file:
        template_str = file.read()
    template_str = re.sub("<version>", core.__version__, template_str)
    with open(yml_path, 'w') as file:
        file.write(template_str)


def create_run_solution(output_path, solution_coordinates):
    with open(pkg_resources.resource_filename('album.package.resources.templates.no_gui', 'run_solution_template.py'),
              'r') as file:
        template_str = file.read()

    base_path = repr(str(Path.home().joinpath('.album', 'envs', 'album')))
    tmp = re.sub(r"\\", r"\\\\", base_path)
    template_str = re.sub("\"<base_path>\"", tmp, template_str)
    template_str = re.sub("<solution>", str(solution_coordinates), template_str)

    with open(Path(output_path).joinpath("run_solution.py"), 'w') as file:
        file.write(template_str)


def create_call_solution(output_path):
    with open(pkg_resources.resource_filename('album.package.resources.templates.no_gui', 'call_solution_template.py'),
              'r') as file:
        template_str = file.read()
    with open(Path(output_path).joinpath("call_solution.py"), 'w') as file:
        file.write(template_str)
