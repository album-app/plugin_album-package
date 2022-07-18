import os
import platform
import re
import subprocess
import sys
import json
from pathlib import Path


def get_solution_list_json(json_str):
    json_str = json.loads(json_str.decode())
    # list
    catalog_list = json_str['catalogs']
    # list of catalogs_list of solution_dicts
    catalog_list_of_solution_lists = []
    # list of dict containing dicts as values
    solution_dicts_list = []

    if isinstance(catalog_list, list):
        for cat_dict in catalog_list:
            catalog_list_of_solution_lists.append(cat_dict['solutions'])
    for solution_list in catalog_list_of_solution_lists:
        for solution in solution_list:
            solution_dicts_list.append(solution)

    return solution_dicts_list


def check_solutions_dict(solution_dicts, coordinates):
    group = coordinates.split(':')[0]
    name = coordinates.split(':')[1]
    version = coordinates.split(':')[2]

    # Go through the list of dictionaries and checking there setup method for the coordinates and then check the internal
    # string for the installation status
    for solution in solution_dicts:
        internal = solution['internal']
        setup = solution['setup']
        installed = internal['installed']
        tmp_group = setup['group']
        tmp_name = setup['name']
        tmp_version = setup['version']
        if (group == tmp_group) and (name == tmp_name) and (version == tmp_version):
            if installed == 1:
                print("solution already installed")
                return True
            else:
                return False

    return False


def get_params(conda, album, coordinates):
    # print the solution information
    if conda and album:
        cmd = subprocess.run(["conda", "run", "-n", "album", "album", "info", coordinates])

    elif conda and not album:
        cmd = subprocess.run(
            ["conda", "run", "-p", str(Path.home().joinpath('.album', 'envs', 'album')), "album", "info", coordinates])

    elif (not conda) and album:
        if platform.system() == 'Windows':
            cmd = subprocess.run(
                [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-n", "album",
                 "album", "info", coordinates])

        else:
            cmd = subprocess.run(
                [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda')), "run", "-n", "album",
                 "album", "info", coordinates])

    elif (not conda) and (not album):
        if platform.system() == 'Windows':
            cmd = subprocess.run(
                [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-p",
                 str(Path.home().joinpath('.album', 'envs', 'album')), "album", "info", coordinates])
        else:
            cmd = subprocess.run(
                [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda')), "run", "-p",
                 str(Path.home().joinpath('.album', 'envs', 'album')), "album", "info", coordinates])
    else:
        sys.exit("Solution isn't probably installed. Please try again.")

    # get input parameter for the solution
    commands = input('Please enter the parameters with which the package solution should be called:')
    # if this script gets called from another Popen subprocess (like from the tests) the communicate function passes
    # input as byte strings which need to be decoded
    if isinstance(commands, bytes):
        commands = commands.decode()
    commands = re.split(r'\s', commands)
    params = ''
    for p in commands:
        params += ' %s' % p
    return params


def installed_check(conda, album, coordinates):
    # conda = true if condas env path var is set
    # album = true if there is an environment named album
    if conda and album:
        # returns json string containing info about all solutions in the local collection database
        cmd = subprocess.run(["conda", "run", "-n", "album", "album", "index", "--json"],
                             capture_output=True)
        # filter json string and check for installation status of active solution
        return check_solutions_dict(get_solution_list_json(cmd.stdout), coordinates)

    elif conda and not album:
        cmd = subprocess.run(
            ["conda", "run", "-p", str(Path.home().joinpath('.album', 'envs', 'album')), "album", "index", "--json"],
            capture_output=True)
        return check_solutions_dict(get_solution_list_json(cmd.stdout), coordinates)

    elif (not conda) and album:
        if platform.system() == 'Windows':
            cmd = subprocess.run(
                [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-n", "album",
                 "album", "index", "--json"], capture_output=True)
            return check_solutions_dict(get_solution_list_json(cmd.stdout), coordinates)

        else:
            cmd = subprocess.run(
                [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda')), "run", "-n", "album",
                 "album", "index", "--json"], capture_output=True)
            return check_solutions_dict(get_solution_list_json(cmd.stdout), coordinates)

    elif (not conda) and (not album):
        if platform.system() == 'Windows':
            cmd = subprocess.run(
                [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-p",
                 str(Path.home().joinpath('.album', 'envs', 'album')), "album", "index", "--json"], capture_output=True)
            return check_solutions_dict(get_solution_list_json(cmd.stdout), coordinates)

        else:
            cmd = subprocess.run(
                [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda')), "run", "-p",
                 str(Path.home().joinpath('.album', 'envs', 'album')), "album", "index", "--json"], capture_output=True)
            return check_solutions_dict(get_solution_list_json(cmd.stdout), coordinates)
    else:
        sys.exit("Couldn't check if the solution is already installed. Please check your conda and album installation.")


def call_named_album_install_conda_path():
    # use a conda which can be called via conda command and an environment called album to install the solution
    cmd = subprocess.run(["conda", "run", "-n", "album", "album", "install",
                          str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files'))], capture_output=True)
    if cmd.returncode != 0:
        print("%s \n %s" % (cmd.stderr, cmd.stdout))
    return cmd.returncode


def call_named_album_run_conda_path(params):
    call = "conda run -n album album run %s%s" % (
        str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')), params)
    call_list = re.split(r'\s', call)
    cmd = subprocess.run(call_list)
    return cmd.returncode


def call_prefixed_album_install_conda_path():
    # use a conda which can be called via conda command and an album environment which got created with prefix and no
    # name to install the solution
    cmd = subprocess.run(
        ["conda", "run", "-p", str(Path.home().joinpath('.album', 'envs', 'album')), "album", "install",
         str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files'))], capture_output=True)
    if cmd.returncode != 0:
        print("%s \n %s" % (cmd.stderr, cmd.stdout))
    return cmd.returncode


def call_prefixed_album_run_conda_path(params):
    call = "conda run -p %s album run %s%s" % (str(Path.home().joinpath('.album', 'envs', 'album')),
                                               str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files',
                                                                                                    'solution.py')),
                                               params)
    call_list = re.split(r'\s', call)
    cmd = subprocess.run(call_list)
    return cmd.returncode


def call_named_album_install_conda_exe():
    # use a conda which installed via the install script and an environment called album to install the solution
    if platform.system() == 'Windows':
        cmd = subprocess.run(
            [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-n", "album", "album",
             "install", str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files'))], capture_output=True)
        if cmd.returncode != 0:
            print("%s \n %s" % (cmd.stderr, cmd.stdout))
        return cmd.returncode
    else:
        cmd = subprocess.run(
            [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-n", "album", "album",
             "install", Path(os.path.realpath(__file__)).parent.joinpath('solution_files')], capture_output=True)
        if cmd.returncode != 0:
            print("%s \n %s" % (cmd.stderr, cmd.stdout))
        return cmd.returncode


def call_named_album_run_conda_exe(params):
    # use a conda which installed via the install script and an environment called album to run the solution
    if platform.system() == 'Windows':
        call = "%s run -n album album run %s%s" % (
        str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')),
        str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')), params)
        call_list = re.split(r'\s', call)
        cmd = subprocess.run(call_list)
        return cmd.returncode
    else:
        call = "%s run -n album album run %s%s" % (
        str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda')),
        str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')), params)
        call_list = re.split(r'\s', call)
        cmd = subprocess.run(call_list)
        return cmd.returncode


def call_prefixed_album_install_conda_exe():
    # use a conda which installed via the install script and an album environment which got created with prefix and no
    #     # name to install the solution
    if platform.system() == 'Windows':
        cmd = subprocess.run([str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-p",
                              str(Path.home().joinpath('.album', 'envs', 'album')), "album", "install",
                              str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files'))],
                             capture_output=True)
        if cmd.returncode != 0:
            print("%s \n %s" % (cmd.stderr, cmd.stdout))
        return cmd.returncode
    else:
        cmd = subprocess.run([Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-p",
                              Path.home().joinpath('.album', 'envs', 'album'), "album", "install",
                              Path(os.path.realpath(__file__)).parent.joinpath('solution_files')])
        if cmd.returncode != 0:
            print("%s \n %s" % (cmd.stderr, cmd.stdout))
        return cmd.returncode


def call_prefixed_album_run_conda_exe(params):
    # use a conda which was installed via the install script and an album environment which got created with prefix and no
    # name to run the solution
    if platform.system() == 'Windows':
        call = "%s run -p %s album run %s%s" % (
        str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')),
        str(Path.home().joinpath('.album', 'envs', 'album')),
        str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')), params)
        call_list = re.split(r'\s', call)
        cmd = subprocess.run(call_list)
        return cmd.returncode
    else:
        call = "%s run -p %s album run %s%s" % (
        str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda')),
        str(Path.home().joinpath('.album', 'envs', 'album')),
        str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')), params)
        call_list = re.split(r'\s', call)
        cmd = subprocess.run(call_list)
        return cmd.returncode


def create_shortcut_script(coordinates,conda):
    if not conda:
        conda_exe = 'str(Path.home().joinpath(\'.album\', \'Miniconda\'))'
    else:
        conda_exe = "\'conda\'"
    # make script which will be called by the shortcut and triggers the solution
    with open(Path(os.path.realpath(__file__)).parent.joinpath('run_solution.template'),
              'r') as file:
        template_str = file.read()
    template_str = re.sub("<solution>", str(coordinates), template_str)
    template_str = re.sub("<conda>", conda_exe, template_str)

    with open(Path(os.path.realpath(__file__)).parent.joinpath('uninstall_solution.template'),
              'r') as file:
        template_str_uninstall = file.read()
    template_str_uninstall = re.sub("<solution>", str(coordinates), template_str_uninstall)
    template_str_uninstall = re.sub("<conda>", conda_exe, template_str_uninstall)

    mod_coords = re.sub(':', '_', coordinates)
    # on macos the coordniates must not contain .'s since the shortcut cannot get the album logo as icon
    if platform.system() == 'Darwin':
        mod_coords = re.sub('\.', '_', mod_coords)

    if not os.path.isdir(Path.home().joinpath('.album', 'Solution_shortcuts')):
        os.mkdir(Path.home().joinpath('.album', 'Solution_shortcuts'))

    if not os.path.isdir(Path.home().joinpath('.album', 'Solution_shortcuts', mod_coords)):
        os.mkdir(Path.home().joinpath('.album', 'Solution_shortcuts', mod_coords))

    if os.path.isfile(Path.home().joinpath('.album', 'Solution_shortcuts', mod_coords ,'run_solution.py')):
        os.remove(Path.home().joinpath('.album', 'Solution_shortcuts', mod_coords ,'run_solution.py'))

    if os.path.isfile(Path.home().joinpath('.album', 'Solution_shortcuts', mod_coords ,'uninstall_solution.py')):
        os.remove(Path.home().joinpath('.album', 'Solution_shortcuts', mod_coords ,'uninstall_solution.py'))

    with open(Path.home().joinpath('.album', 'Solution_shortcuts', mod_coords ,'run_solution.py'), 'w') as file:
        file.write(template_str)

    with open(Path.home().joinpath('.album', 'Solution_shortcuts', mod_coords ,'uninstall_solution.py'), 'w') as file:
        file.write(template_str_uninstall)


def create_shortcut(coordinates, conda, album):
    #from pyshortcuts import make_shortcut
    mod_coords = re.sub(':', '_', coordinates)
    # on macos the coordniates must not contain .'s since the shortcut cannot get the album logo as icon
    if platform.system() == 'Darwin':
        mod_coords = re.sub('\.', '_', mod_coords)
    run_name = 'run_%s' % mod_coords
    run_path = str(Path.home().joinpath('.album', 'Solution_shortcuts', mod_coords, 'run_solution.py'))
    uninstall_name = 'uninstall_%s' % mod_coords
    uninstall_path = str(Path.home().joinpath('.album', 'Solution_shortcuts', mod_coords, 'uninstall_solution.py'))


    if platform.system() == 'Windows':
        icon_path = str(Path.home().joinpath('.album', 'Solution_shortcuts', 'album_icon_windows.ico'))
    elif platform.system() == 'Darwin':
        icon_path = str(Path.home().joinpath('.album', 'Solution_shortcuts', 'album_icon_macos.icns'))
    elif platform.system() == 'Linux':
        icon_path = str(Path.home().joinpath('.album', 'Solution_shortcuts', 'album_icon_linux.png'))
    else:
        print("Your OS is currently not supported")
        raise NotImplementedError

    # get path of python interpreter of the album env
    if album:
        if conda:
            cmd = subprocess.run(['conda', 'run', '-n', 'album', 'conda', 'info'], capture_output=True)
            out = cmd.stdout.decode()
            tmp = out.split('\n')[2]
            tmp = tmp.split('\r')[0]
            tmp = tmp.split(': ')[1]
            if platform.system() == 'Windows':
                python_path = str(Path(tmp).joinpath('python.exe'))
            else:
                python_path = str(Path(tmp).joinpath('bin', 'python'))
            cmd_run_shortcut = subprocess.run(
                ['conda', 'run', '-n', 'album', 'pyshortcut', '-n', run_name, '-i', icon_path, '-e', python_path,
                 run_path])
            cmd_uninstall_shortcut = subprocess.run(
                ['conda', 'run', '-n', 'album', 'pyshortcut', '-n', uninstall_name, '-i', icon_path, '-e',
                 python_path,
                 uninstall_path])
        else:
            try:
                if platform.system() == 'Windows':
                    # perform a conda info inside the album env to get the location of the album env and with that the
                    # location of the python of the album env
                    cmd = subprocess.run([str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')),
                                          'run', '-n', 'album', str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), 'info'], capture_output=True)
                    out = cmd.stdout.decode()
                    tmp = out.split('\n')[2]
                    tmp = tmp.split('\r')[0]
                    tmp = tmp.split(': ')[1]
                    python_path = str(Path(tmp).joinpath('python.exe'))

                    cmd_run_shortcut = subprocess.run(
                        [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), 'run', '-n',
                         'album', 'pyshortcut', '-n', run_name, '-i', icon_path, '-e', python_path, run_path])
                    cmd_uninstall_shortcut = subprocess.run(
                        [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), 'run', '-n',
                         'album', 'pyshortcut', '-n', uninstall_name, '-i', icon_path, '-e', python_path,
                         uninstall_path])

                else:
                    cmd = subprocess.run([str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda')),
                                          'run', '-n', 'album',
                                          str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda')),
                                          'info'], capture_output=True)
                    out = cmd.stdout.decode()
                    tmp = out.split('\n')[2]
                    tmp = tmp.split('\r')[0]
                    tmp = tmp.split(': ')[1]
                    python_path = str(Path(tmp).joinpath('bin', 'python'))

                    cmd_run_shortcut = subprocess.run(
                        [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda')), 'run', '-n',
                         'album', 'pyshortcut', '-n', run_name, '-i', icon_path, '-e', python_path, run_path])
                    cmd_uninstall_shortcut = subprocess.run(
                        [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda')), 'run', '-n',
                         'album', 'pyshortcut', '-n', uninstall_name, '-i', icon_path, '-e', python_path, uninstall_path])

            except Exception:
                sys.exit('There was a Problem with your Album env. There seams to be env called Album but no conda installation lists it.')
    else:
        if conda:
            if platform.system() == 'Windows':
                python_path = str(Path.home().joinpath('.album', 'envs', 'album', 'python.exe'))
            else:
                python_path = str(Path.home().joinpath('.album', 'envs', 'album', 'bin', 'python'))
            cmd_run_shortcut = subprocess.run(
                ['conda', 'run', '-p', str(Path.home().joinpath('.album', 'envs', 'album')), 'pyshortcut', '-n', run_name, '-i', icon_path, '-e', python_path,
                 run_path])
            cmd_uninstall_shortcut = subprocess.run(
                ['conda', 'run', '-p', str(Path.home().joinpath('.album', 'envs', 'album')), 'pyshortcut', '-n', uninstall_name, '-i', icon_path, '-e',
                 python_path,
                 uninstall_path])
        else:
            if platform.system() == 'Windows':
                python_path = str(Path.home().joinpath('.album', 'envs', 'album', 'python.exe'))
                conda_exe = str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat'))
            else:
                python_path = str(Path.home().joinpath('.album', 'envs', 'album', 'bin', 'python'))
                conda_exe = str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'))
            cmd_run_shortcut = subprocess.run(
                [conda_exe, 'run', '-p', str(Path.home().joinpath('.album', 'envs', 'album')) , 'pyshortcut', '-n', run_name, '-i', icon_path, '-e', python_path,
                 run_path])
            cmd_uninstall_shortcut = subprocess.run(
                [conda_exe, 'run', '-p', str(Path.home().joinpath('.album', 'envs', 'album')), 'pyshortcut', '-n', uninstall_name, '-i', icon_path, '-e',
                 python_path,
                 uninstall_path])

    #make_shortcut(str(Path.home().joinpath('.album', 'Solution_shortcuts', mod_coords ,'run_solution.py')), name='run_%s' %mod_coords, icon=icon_path, executable=python_path)
    #make_shortcut(str(Path.home().joinpath('.album', 'Solution_shortcuts', mod_coords ,'uninstall_solution.py')), name='uninstall_%s' %mod_coords, icon=icon_path, executable=python_path)


def main():
    coordinates = '<coordinates>'

    # exeption if conda is missing
    try:
        # check if there is an env present with the name album and a conda installation with path env var
        cmd = subprocess.run(["conda", "run", "-n", "album", "album", "-h"], capture_output=True)
        # returncode != 0 if something is not right with album
        #print("!! 1 %s !!" % cmd.returncode)
        if cmd.returncode == 0:
            install_return = 0
            if not installed_check(conda=True, album=True, coordinates=coordinates):
                print('Solution is not installed. Installing...')
                install_return = call_named_album_install_conda_path()
            if install_return != 0:
                sys.exit("There was an error installing the solution!")
            create_shortcut_script(coordinates, conda=True)
            create_shortcut(conda=True, album=True, coordinates=coordinates)

        else:
            # check if there is an album env with prefix and a conda installation with path env var
            cmd = subprocess.run(
                ["conda", "run", "-p", str(Path.home().joinpath('.album', 'envs', 'album')), "album", "-h"],
                capture_output=True)
            #print("!!!2! %s!!" % cmd.returncode)
            if cmd.returncode == 0:
                install_return = 0
                if not installed_check(conda=True, album=False, coordinates=coordinates):
                    print('Solution is not installed. Installing...')
                    install_return = call_prefixed_album_install_conda_path()
                if install_return != 0:
                    sys.exit("There was an error installing the solution!")
                create_shortcut_script(coordinates, conda=True)
                create_shortcut(conda=True, album=False, coordinates=coordinates)

            else:
                sys.exit(
                    "Could not find album to run the solution. Please check your album installation.")
    # TODO: try exception subprocess.CalledProcessError and run(check=True) as replacement for Exception
    except Exception as e:
        try:
            if platform.system() == 'Windows':
                # check if there is an env present with the name album and a conda installation in the album base dir
                cmd = subprocess.run(
                    [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-n", "album",
                     "album",
                     "-h"], capture_output=True)
                #print("3 %s" % cmd.returncode)
                if cmd.returncode == 0:
                    install_return = 0
                    if not installed_check(conda=False, album=True, coordinates=coordinates):
                        print('Solution is not installed. Installing...')
                        install_return = call_named_album_install_conda_exe()
                    if install_return != 0:
                        sys.exit("There was an error installing the solution!")

                    create_shortcut_script(coordinates, conda=False)
                    create_shortcut(conda=False, album=True, coordinates=coordinates)

                else:
                    # check if there is an album env present with the install script prefix and
                    # a conda installation in the album base dir
                    cmd = subprocess.run(
                        [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-p",
                         str(Path.home().joinpath('.album', 'envs', 'album')), "album", "-h"],
                        capture_output=True)
                    #print("4 %s" % cmd.returncode)
                    if cmd.returncode == 0:
                        install_return = 0
                        if not installed_check(conda=False, album=False, coordinates=coordinates):
                            print('Solution is not installed. Installing...')
                            install_return = call_prefixed_album_install_conda_exe()
                        if install_return != 0:
                            sys.exit("There was an error installing the solution!")

                        create_shortcut_script(coordinates, conda=False)
                        create_shortcut(conda=False, album=False, coordinates=coordinates)

                    else:
                        print(
                            "Could not find album to run the solution. Please check your album installation.")

            else:
                # check if there is an env present with the name album and a conda installation in the album base dir
                cmd = subprocess.run(
                    [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-n", "album",
                     "album",
                     "-h"], capture_output=True)
                #print("3 %s" % cmd.returncode)
                if cmd.returncode == 0:
                    install_return = 0
                    if not installed_check(conda=False, album=True, coordinates=coordinates):
                        print('Solution is not installed. Installing...')
                        install_return = call_named_album_install_conda_exe()
                    if install_return != 0:
                        sys.exit("There was an error installing the solution!")
                    create_shortcut_script(coordinates, conda=False)
                    create_shortcut(conda=False, album=True, coordinates=coordinates)

                else:
                    # check if there is an album env present with the install script prefix and
                    # a conda installation in the album base dir
                    cmd = subprocess.run(
                        [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-p",
                         Path.home().joinpath('.album', 'envs', 'album'), "album", "-h"],
                        capture_output=True)
                    #print("4%s" % cmd.returncode)
                    if cmd.returncode == 0:
                        install_return = 0
                        if not installed_check(conda=False, album=False, coordinates=coordinates):
                            print('Solution is not installed. Installing...')
                            install_return = call_prefixed_album_install_conda_exe()
                        if install_return != 0:
                            sys.exit("There was an error installing the solution!")
                        create_shortcut_script(coordinates, conda=False)
                        create_shortcut(conda=False, album=False, coordinates=coordinates)

                    else:
                        sys.exit(
                            "Could not find album to run the solution. Please check your album installation.")

        except Exception as e:
            sys.exit(
                "An unexpected Error occured when runnig the solution. Please check your conda installation: %s" % e)


if __name__ == "__main__":
    main()
