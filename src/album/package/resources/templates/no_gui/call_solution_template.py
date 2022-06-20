import os
import platform
import re
from pathlib import Path
import subprocess
import shutil

#commands = input('Please enter the parameters with which the package solution should be called:')
#commands = re.split(r'\s', commands)
params = ''
#for p in commands:
#    params += ' %s' %p

try:
    conda_check = subprocess.check_output('conda info')
    cmd = subprocess.run(["conda", "run", "-n", "album", "album", "index"],capture_output=True)
    print(cmd.returncode)
    print(cmd.stderr)
    print(cmd.stdout)
    if cmd.returncode == 0:
        cmd2= subprocess.run(["conda", "run", "-n", 'album', "album", "install",
                         Path(os.path.realpath(__file__)).parent.joinpath('solution_files')],capture_output=True)
        print("2")
        print(cmd2.returncode)
        print(cmd2.stderr)
        print(cmd2.stdout)
        cmd3= subprocess.run(["conda", "run", "-n", 'album', "album", "run",
                         Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py'), params],capture_output=True)
        print("3")
        print(cmd3.returncode)
        print(cmd3.stderr)
        print(cmd3.stdout)
    else:
        cmd4 = subprocess.run(["conda", "run", "-p", Path.home().joinpath('.album', 'envs', 'album'), "album", "install",
                         Path(os.path.realpath(__file__)).parent.joinpath('solution_files')],capture_output=True)
        print("4")
        print(cmd4.returncode)
        print(cmd4.stderr)
        print(cmd4.stdout)
        cmd5 = subprocess.run(
            ["conda", "run", "-p", Path.home().joinpath('.album', 'envs', 'album'), "album", "run",
             Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py'), params],capture_output=True)
        print("5")
        print(cmd5.returncode)
        print(cmd5.stderr)
        print(cmd5.stdout)
except Exception as e:
    if platform.system() == 'Windows':
        cmd = subprocess.run(
            [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat'), "run", "-n", "album", "album",
             "index"],capture_output=True)
        print("1.1")
        print(cmd.returncode)
        print(cmd.stderr)
        print(cmd.stdout)

        if cmd.returncode == 0:
            cmd6 =subprocess.run(
                [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat'), "run", "-n", 'album', "album",
                 "install", Path(os.path.realpath(__file__)).parent.joinpath('solution_files')],capture_output=True)
            print("6")
            print(cmd6.returncode)
            print(cmd6.stderr)
            print(cmd6.stdout)
            cmd7=subprocess.run(
                [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat'), "run", "-n", 'album', "album",
                 "run", Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py'), params],capture_output=True)
            print("7")
            print(cmd7.returncode)
            print(cmd7.stderr)
            print(cmd7.stdout)
        else:
            cmd8=subprocess.run([Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat'), "run", "-p",
                             Path.home().joinpath('.album', 'envs', 'album'), "album", "install",
                             Path(os.path.realpath(__file__)).parent.joinpath('solution_files')],capture_output=True)
            print("8")
            print(cmd8.returncode)
            print(cmd8.stderr)
            print(cmd8.stdout)
            cmd9=subprocess.run([Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat'), "run", "-p",
                             Path.home().joinpath('.album', 'envs', 'album'), "album", "run",
                             Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py'), params],capture_output=True)
            print("9")
            print(cmd9.returncode)
            print(cmd9.stderr)
            print(cmd9.stdout)
    else:
        cmd = subprocess.run(
            [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-n", "album", "album",
             "index"])
        print("1.3")
        print(cmd.returncode)
        print(cmd.stderr)
        print(cmd.stdout)
        if cmd.returncode == 0:
            cmd10=subprocess.run(
                [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-n", 'album', "album",
                 "install", Path(os.path.realpath(__file__)).parent.joinpath('solution_files')],capture_output=True)
            print("10")
            print(cmd10.returncode)
            print(cmd10.stderr)
            print(cmd10.stdout)
            cmd11=subprocess.run(
                [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-n", 'album', "album", "run",
                 Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py'), params],capture_output=True)
            print("11")
            print(cmd11.returncode)
            print(cmd11.stderr)
            print(cmd11.stdout)
        else:
            cmd12=subprocess.run([Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-p",
                             Path.home().joinpath('.album', 'envs', 'album'), "album", "install",
                             Path(os.path.realpath(__file__)).parent.joinpath('solution_files')],capture_output=True)
            print("12")
            print(cmd12.returncode)
            print(cmd12.stderr)
            print(cmd12.stdout)
            cmd13=subprocess.run([Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-p",
                             Path.home().joinpath('.album', 'envs', 'album'), "album", "run",
                             Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py'), params],capture_output=True)
            print("13")
            print(cmd13.returncode)
            print(cmd13.stderr)
            print(cmd13.stdout)


