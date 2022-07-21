import re
import shutil

from pathlib import Path
from album import core

import pkg_resources


def create(output_path, coordinates, no_gui):
    create_yml(output_path)
    if no_gui:
        create_call_solution_no_gui(output_path, coordinates)
    else:
        create_call_solution_gui(output_path, coordinates)


def create_yml(output_path):
    yml_path = Path(output_path).joinpath('album.yml')
    with open(pkg_resources.resource_filename('album.package.resources.templates', 'album.yml'), 'r') as file:
        template_str = file.read()
    template_str = re.sub("<version>", core.__version__, template_str)
    with open(yml_path, 'w') as file:
        file.write(template_str)


def create_call_solution_gui(output_path, coordinates):
    with open(pkg_resources.resource_filename('album.package.resources.templates.gui', 'call_solution_gui_template.py'),
              'r') as file:
        template_str = file.read()
    template_str = re.sub("<coordinates>", str(coordinates), template_str)
    with open(Path(output_path).joinpath('call_solution.py'), 'w') as file:
        file.write(template_str)


def create_call_solution_no_gui(output_path, coordinates):
    with open(pkg_resources.resource_filename('album.package.resources.templates.no_gui', 'call_solution_template.py'),
              'r') as file:
        template_str = file.read()
    template_str = re.sub("<coordinates>", str(coordinates), template_str)
    with open(Path(output_path).joinpath('call_solution.py'), 'w') as file:
        file.write(template_str)
