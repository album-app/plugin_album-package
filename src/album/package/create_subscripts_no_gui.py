import re
from pathlib import Path
from album import core

import pkg_resources


def create(output_path, solution_coordinates):
    create_yml(output_path)
    create_run_solution(output_path, solution_coordinates)
    create_call_solution(output_path)


def create_run_solution(output_path, solution_coordinates):
    run_solution_path = Path(output_path).joinpath('run_solution.py')
    file = open(run_solution_path, "w", encoding='utf-8')
    file.write('from album.api import Album\n')
    file.write('import os\n')
    file.write('import sys\n')
    file.write('import re\n')
    file.write('from pathlib import Path\n')
    file.write('import subprocess\n')
    file.write('sol_dir = ')
    file.write('Path(os.path.realpath(__file__)).parent.parent.joinpath(\'solution_files\')\n')
    file.write('album = Album.Builder().base_cache_path(')
    file.write(repr(str(Path.home().joinpath('.album', 'envs', 'album'))))
    file.write(').build()\n')
    file.write('album.load_or_create_collection()\n')
    file.write('if not album.is_installed(sol_dir):\n')
    file.write('\talbum.install(sol_dir)\n')
    file.write('commands = input(\'Please enter the parameters with which the package solution should be '
               'called:\')\n')
    file.write('commands = re.split(r\'\\s\', commands)\n')
    file.write('params = [\'\']\n')
    file.write('for p in commands:\n')
    file.write('\tparams.append(p)\n')
    file.write('album.run(\'')
    file.write(str(solution_coordinates))
    file.write('\',params)\n')
    file.close()


def create_call_solution(output_path):
    executer_path = Path(output_path).joinpath('call_solution.py')

    file = open(executer_path, "w", encoding='utf-8')
    file.write('import os\n')
    file.write('from pathlib import Path\n')
    file.write('import subprocess\n')
    file.write('import shutil\n')
    file.write('conda_path = shutil.which(\"conda\")\n')
    file.write('env_path = Path.home().joinpath(\'.album\', \'envs\', \'album\')\n')
    file.write('python_path = Path.home().joinpath(\'.album\', \'envs\', \'album\', '
               '\'python\')\n')
    file.write('run_sol_path =')
    file.write('Path(os.path.realpath(__file__)).parent.joinpath(\'subscripts\', \'run_solution.py\')')
    file.write('\n')
    file.write('python_call = \'%s %s\' %(python_path, run_sol_path)\n')
    file.write('subprocess.call(python_call)\n')
    file.close()


def create_yml(output_path):
    yml_path = Path(output_path).joinpath('album.yml')
    with open(pkg_resources.resource_filename('album.package.resources', 'album.yml'), 'r') as file:
        template_str = file.read()
    template_str = re.sub("<version>", core.__version__, template_str)
    with open(yml_path, 'w') as file:
        file.write(template_str)
