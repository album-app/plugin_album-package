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
    #string for the installation status
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


def get_params(coordinates):
    # get input parameter for the solution
    group = coordinates.split(':')[0]
    name = coordinates.split(':')[1]
    version = coordinates.split(':')[2]
    args_list = []

    # get json comntaining info of all solutions of the local collection
    cmd = subprocess.run(["conda", "run", "-n", "album", "album", "index", "--json"],
                         capture_output=True)
    solution_dicts = get_solution_list_json(cmd.stdout)
    # filter for active solution and get the arguments of the solution
    for solution in solution_dicts:
        setup = solution['setup']
        tmp_group = setup['group']
        tmp_name = setup['name']
        tmp_version = setup['version']
        if (group == tmp_group) and (name == tmp_name) and (version == tmp_version):
            args_list = setup['args']

    # output solution arguments
    print("\nThe parameters of the solution are the following:\n")
    for arg in args_list:
        print("--%s" % arg['name'])
        print(arg['description'])
        print("type: %s" % arg['type'])
        print("\n")


    commands = input('Please enter the parameters with which the package solution should be called:')
    # if this script gets called from another Popen subprocess (like from the tests) the communicate function passes
    # input as byte strings which need to be decoded
    if isinstance(commands, bytes):
        commands = commands.decode()
    commands = re.split(r'\s', commands)
    params = ''
    for p in commands:
        params += ' %s' % p
    print(params)
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
    # use a conda which can be called via conda command and an environment called album to run the solution
    cmd = subprocess.run(["conda", "run", "-n", "album", "album", "run",
                          str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')),
                          params])
    return cmd.returncode


def call_prefixed_album_install_conda_path():
    # use a conda which can be called via conda command and an album environment which got created with prefix and no
    # name to install the solution
    cmd = subprocess.run(
        ["conda", "run", "-p", str(Path.home().joinpath('.album', 'envs', 'album')), "album", "install",
         str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files'))], capture_output=True)
    return cmd.returncode


def call_prefixed_album_run_conda_path(params):
    # use a conda which can be called via conda command and an album environment which got created with prefix and no
    # name to run the solution
    cmd = subprocess.run(
        ["conda", "run", "-p", str(Path.home().joinpath('.album', 'envs', 'album')), "album", "run",
         str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')), params])
    return cmd.returncode


def call_named_album_install_conda_exe():
    # use a conda which installed via the install script and an environment called album to install the solution
    if platform.system() == 'Windows':
        cmd = subprocess.run(
            [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-n", "album", "album",
             "install", str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files'))], capture_output=True)
        return cmd.returncode
    else:
        cmd = subprocess.run(
            [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-n", "album", "album",
             "install", Path(os.path.realpath(__file__)).parent.joinpath('solution_files')], capture_output=True)
        return cmd.returncode


def call_named_album_run_conda_exe(params):
    # use a conda which installed via the install script and an environment called album to run the solution
    if platform.system() == 'Windows':
        cmd = subprocess.run(
            [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-n", "album", "album",
             "run", str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')), params])
        return cmd.returncode
    else:
        cmd = subprocess.run(
            [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-n", "album", "album", "run",
             Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py'), params])
        return cmd.returncode


def call_prefixed_album_install_conda_exe():
    # use a conda which installed via the install script and an album environment which got created with prefix and no
    #     # name to install the solution
    if platform.system() == 'Windows':
        cmd = subprocess.run([str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-p",
                              str(Path.home().joinpath('.album', 'envs', 'album')), "album", "install",
                              str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files'))],
                             capture_output=True)
        return cmd.returncode
    else:
        cmd = subprocess.run([Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-p",
                              Path.home().joinpath('.album', 'envs', 'album'), "album", "install",
                              Path(os.path.realpath(__file__)).parent.joinpath('solution_files')])
        print(cmd.returncode)
        return cmd.returncode


def call_prefixed_album_run_conda_exe(params):
    # use a conda which was installed via the install script and an album environment which got created with prefix and no
    # name to run the solution
    if platform.system() == 'Windows':
        cmd = subprocess.run([str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-p",
                              str(Path.home().joinpath('.album', 'envs', 'album')), "album", "run",
                              str(Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py')),
                              params])
        return cmd.returncode
    else:
        cmd = subprocess.run([Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-p",
                              Path.home().joinpath('.album', 'envs', 'album'), "album", "run",
                              Path(os.path.realpath(__file__)).parent.joinpath('solution_files', 'solution.py'),
                              params])
        return cmd.returncode


def main():
    coordinates = '<coordinates>'

    # exeption if conda is missing
    try:
        # check if there is an env present with the name album and a conda installation with path env var
        cmd = subprocess.run(["conda", "run", "-n", "album", "album", "-h"], capture_output=True)
        # returncode != 0 if something is not right with album
        print("1%s" % cmd.returncode)
        if cmd.returncode == 0:
            install_return = 0
            if not installed_check(conda=True, album=True, coordinates=coordinates):
                print('Solution is not installed. Installing...')
                install_return = call_named_album_install_conda_path()
            if install_return != 0:
                sys.exit("There was an error installing the solution!")
            params = get_params(coordinates)
            call_return = call_named_album_run_conda_path(params)
            if call_return != 0:
                sys.exit("There was an error running the solution!")

        else:
            # check if there is an album env with prefix and a conda installation with path env var
            cmd = subprocess.run(
                ["conda", "run", "-p", str(Path.home().joinpath('.album', 'envs', 'album')), "album", "-h"],
                capture_output=True)
            print("2! %s" % cmd.returncode)
            if cmd.returncode == 0:
                install_return = 0
                if not installed_check(conda=True, album=False, coordinates=coordinates):
                    print('Solution is not installed. Installing...')
                    install_return = call_prefixed_album_install_conda_path()
                if install_return != 0:
                    sys.exit("There was an error installing the solution!")
                params = get_params(coordinates)
                call_return = call_prefixed_album_run_conda_path(params)
                if call_return != 0:
                    sys.exit("There was an error running the solution!")

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
                print("3 %s" % cmd.returncode)
                if cmd.returncode == 0:
                    install_return = 0
                    if not installed_check(conda=False, album=True, coordinates=coordinates):
                        print('Solution is not installed. Installing...')
                        install_return = call_named_album_install_conda_exe()
                    if install_return != 0:
                        sys.exit("There was an error installing the solution!")
                    params = get_params(coordinates)
                    call_return = call_named_album_run_conda_exe(params)
                    if call_return != 0:
                        sys.exit("There was an error running the solution!")

                else:
                    # check if there is an album env present with the install script prefix and
                    # a conda installation in the album base dir
                    cmd = subprocess.run(
                        [str(Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda.bat')), "run", "-p",
                         str(Path.home().joinpath('.album', 'envs', 'album')), "album", "-h"],
                        capture_output=True)
                    print("4%s" % cmd.returncode)
                    if cmd.returncode == 0:
                        install_return = 0
                        if not installed_check(conda=False, album=False, coordinates=coordinates):
                            print('Solution is not installed. Installing...')
                            install_return = call_prefixed_album_install_conda_exe()
                        if install_return != 0:
                            sys.exit("There was an error installing the solution!")
                        params = get_params(coordinates)
                        call_return = call_prefixed_album_run_conda_exe(params)
                        if call_return != 0:
                            sys.exit("There was an error running the solution!")

                    else:
                        print(
                            "Could not find album to run the solution. Please check your album installation.")

            else:
                # check if there is an env present with the name album and a conda installation in the album base dir
                cmd = subprocess.run(
                    [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-n", "album",
                     "album",
                     "-h"], capture_output=True)
                print("3 %s" % cmd.returncode)
                if cmd.returncode == 0:
                    install_return = 0
                    if not installed_check(conda=False, album=True, coordinates=coordinates):
                        print('Solution is not installed. Installing...')
                        install_return = call_named_album_install_conda_exe()
                    if install_return != 0:
                        sys.exit("There was an error installing the solution!")
                    params = get_params(coordinates)
                    call_return = call_named_album_run_conda_exe(params)
                    if call_return != 0:
                        sys.exit("There was an error running the solution!")

                else:
                    # check if there is an album env present with the install script prefix and
                    # a conda installation in the album base dir
                    cmd = subprocess.run(
                        [Path.home().joinpath('.album', 'Miniconda', 'condabin', 'conda'), "run", "-p",
                         Path.home().joinpath('.album', 'envs', 'album'), "album", "-h"],
                        capture_output=True)
                    print("4%s" % cmd.returncode)
                    if cmd.returncode == 0:
                        install_return = 0
                        if not installed_check(conda=False, album=False, coordinates=coordinates):
                            print('Solution is not installed. Installing...')
                            install_return = call_prefixed_album_install_conda_exe()
                        if install_return != 0:
                            sys.exit("There was an error installing the solution!")
                        params = get_params(coordinates)
                        call_return = call_prefixed_album_run_conda_exe(params)
                        if call_return != 0:
                            sys.exit("There was an error running the solution!")

                    else:
                        sys.exit(
                            "Could not find album to run the solution. Please check your album installation.")

        except Exception as e:
            sys.exit(
                "An unexpected Error occured when runnig the solution. Please check your conda installation: %s" % e)


if __name__ == "__main__":
    main()
