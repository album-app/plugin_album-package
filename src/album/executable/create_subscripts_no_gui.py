import os
import platform
import subprocess
from pathlib import Path


# hier sollen die run_solution , execute_solution und install_hook scripte erstellt und zurückgegeben werden

def run(output_path, solution_coordinates):
    create_hook(output_path)
    create_run_solution(output_path, solution_coordinates)
    create_execute_solution(output_path)


def create_hook(output_path):
    if platform.system() == 'Windows':
        install_script_name = 'install_album_win64.bat'
    elif platform.system() == 'Linux':
        install_script_name = 'install_album_linux64.sh'
    elif platform.system() == 'Darwin':
        install_script_name = 'install_album_macos.sh'

    hook_path = Path(output_path).joinpath('install_hook.py')

    file = open(hook_path, "w", encoding='utf-8')
    file.write('import os\n')
    file.write('from pathlib import Path\n')
    file.write('import subprocess\n')
    file.write('if not (os.path.isdir(Path.home().joinpath(\'.album\',\'env\'))):\n')
    file.write('\tprint("Album missing, installing album.....")\n')
    file.write('\tsubprocess.call([Path(os.path.realpath(__file__)).parent.joinpath(\'')
    file.write(str(install_script_name))
    file.write('\')])\n')
    file.write('else:\n')
    file.write('\tprint("Found Album. Proceeding to run the solution.")\n')
    file.close()

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
    file.write(repr(str(Path.home().joinpath('.album', 'env', 'album'))))
    file.write(').build()\n')
    file.write('album.load_or_create_collection()\n')
    file.write('if not album.is_installed(sol_dir):\n')
    file.write('\talbum.install(sol_dir)\n')
    file.write('commands = input(\'Please enter the parameters with which the executable solution should be '
               'called:\')\n')
    file.write('commands = re.split(r\'\\s\', commands)\n')
    file.write('params = [\'\']\n')
    file.write('for p in commands:\n')
    file.write('\tparams.append(p)\n')
    file.write('album.run(\'')
    file.write(str(solution_coordinates))
    file.write('\',params)\n')
    file.close()

def create_execute_solution(output_path):
    executer_path = Path(output_path).joinpath('execute_solution.py')

    file = open(executer_path, "w", encoding='utf-8')
    file.write('import os\n')
    file.write('from pathlib import Path\n')
    file.write('import subprocess\n')
    file.write('import shutil\n')
    file.write('conda_path = shutil.which(\"conda\")\n')
    file.write('env_path = Path.home().joinpath(\'.album\', \'env\', \'album\')\n')
    file.write('python_path = Path.home().joinpath(\'.album\', \'env\', \'album\', '
               '\'python\')\n')
    file.write('run_sol_path =')
    file.write('Path(os.path.realpath(__file__)).parent.joinpath(\'subscripts\', \'run_solution.py\')')
    file.write('\n')
    file.write('python_call = \'%s %s\' %(python_path, run_sol_path)\n')
    file.write('subprocess.call(python_call)\n')
    file.close()
