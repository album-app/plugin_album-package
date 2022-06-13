import re

from pathlib import Path
from album import core

import pkg_resources


def create(output_path):
    create_yml(output_path)
    create_call_solution(output_path)


def create_call_solution(output_path):
    executer_path = Path(output_path).joinpath('call_solution_gui.py')

    file = open(executer_path, "w", encoding='utf-8')
    file.write('import os\n')
    file.write('from pathlib import Path\n')
    file.write('import subprocess\n')
    file.write('from subprocess import check_output\n')
    file.write('import re\n')
    file.write('try:\n')
    file.write('\tconda_check = check_output(\'conda info\')\n')
    file.write('\tsubprocess.call([\"conda\", \"run\", \"-p\", Path.home().joinpath(\'.album\', '
               '\'envs\', \'album\'), \"album\", \"install\", Path(os.path.realpath('
               '__file__)).parent.joinpath(\'solution_files\')])\n')
    file.write('\tsubprocess.call([\"conda\", \"run\", \"-p\", Path.home().joinpath(\'.album\', '
               '\'envs\', \'album\'), \"album\", \"gui\", \"--solution\", Path(os.path.realpath('
               '__file__)).parent.joinpath(\'solution_files\', \'solution.py\')])\n')
    file.write('except Exception as e:\n')
    file.write('\tsubprocess.call([Path.home().joinpath(\'.album\',\'Miniconda\','
               '\'_conda\'), \"run\", \"-p\", Path.home().joinpath(\'.album\', '
               '\'envs\', \'album\'), \"album\", \"install\", Path(os.path.realpath('
               '__file__)).parent.joinpath(\'solution_files\')])\n')
    file.write('\tsubprocess.call([Path.home().joinpath(\'.album\',\'Miniconda\','
               '\'_conda\'), \"run\", \"-p\", Path.home().joinpath(\'.album\', '
               '\'envs\', \'album\'), \"album\", \"gui\", \"--solution\", Path(os.path.realpath('
               '__file__)).parent.joinpath(\'solution_files\', \'solution.py\')])\n')
    file.close()


def create_yml(output_path):
    yml_path = Path(output_path).joinpath('album.yml')
    with open(pkg_resources.resource_filename('album.package.resources', 'album.yml'), 'r') as file:
        template_str = file.read()
    template_str = re.sub("<version>", core.__version__, template_str)
    with open(yml_path, 'w') as file:
        file.write(template_str)
