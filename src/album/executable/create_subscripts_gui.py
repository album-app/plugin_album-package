import platform

from pathlib import Path


# hier sollen die run_solution , execute_solution und install_hook scripte erstellt und zurückgegeben werden

def run(output_path):
    create_hook(output_path)
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
    file.write(
        'if not (os.path.isdir(Path(os.path.expanduser(\'~\')).joinpath(\'.album\', \'env\'))) or not (os.path.isdir('
        'Path(os.path.expanduser(\'~\')).joinpath(\'.album\', \'env\', \'album\', \'Lib\', \'site-packages\', '
        '\'album\', \'gui\'))):\n')
    file.write('\tprint("Album or Album Gui is missing, installing the missing component.....")\n')
    file.write('\tsubprocess.call([Path(os.path.realpath(__file__)).parent.joinpath(\'')
    file.write(str(install_script_name))
    file.write('\')])\n')
    # Muesste jetzt vom install script gemacht werden.
    # file.write('\tsubprocess.call([Path(os.path.realpath(__file__)).joinpath(\'album\',\'miniconda3\','
    #           '\'_conda.exe\'), \"run\",\"-p\", Path(os.path.realpath(__file__)).parent.joinpath(\'album\', '
    #           '\'env\', \'album\'),\"pip\", \"install\", '
    #           '\" https://gitlab.com/album-app/plugins/album-gui/-/archive/main/album-gui-main.zip\"])\n')
    file.write('else:\n')
    file.write('\tprint("Found Album. Proceeding to run the solution.")\n')
    file.close()


def create_execute_solution(output_path):
    executer_path = Path(output_path).joinpath('execute_solution_gui.py')

    file = open(executer_path, "w", encoding='utf-8')
    file.write('import os\n')
    file.write('from pathlib import Path\n')
    file.write('import subprocess\n')
    file.write('from subprocess import check_output\n')
    file.write('import re\n')
    file.write('album_path = Path(os.path.expanduser(\'~\')).joinpath(\'.album\', \'env\', \'album\', '
               '\'Scripts\',\'album.exe\')\n')
    file.write('album_str = \'%s\'%album_path\n')
    file.write('conda_check = check_output(\'conda info\')\n')
    file.write('conda_check = conda_check.decode()\n')
    file.write('conda_result = re.search(\'base environment : \S+\',conda_check)\n')
    file.write('if conda_result:\n')
    file.write('\tconda_path = re.split(\': \',conda_result.group(0))[1]\n')
    file.write('\tsubprocess.call([Path(conda_path).joinpath('
               '\'_conda.exe\'), \"run\", \"-p\", Path(os.path.expanduser(\'~\')).joinpath(\'.album\', '
               '\'env\', \'album\'), album_str, \"gui\", \"--solution\", Path(os.path.realpath('
               '__file__)).parent.joinpath(\'solution_files\', \'solution.py\')])\n')
    file.write('else:\n')
    file.write('\tsubprocess.call([Path(os.path.expanduser(\'~\')).joinpath(\'miniconda3\','
               '\'_conda.exe\'), \"run\", \"-p\", Path(os.path.expanduser(\'~\')).parent.joinpath(\'.album\', '
               '\'env\', \'album\'), album_str, \"gui\", \"--solution\", Path(os.path.realpath('
               '__file__)).parent.joinpath(\'solution_files\', \'solution.py\')])\n')
    file.close()
