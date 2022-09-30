import inspect
import os
import re
import sys
import unittest.mock
from argparse import Namespace
from pathlib import Path

import pkg_resources

from album.argument_parsing import create_parser
from album.package.argument_parsing import album_package
from album.package.build_executable import fill_placeholder, create_pyinstaller_params
from test_package.test_common import TestCommon


class TestUnitBuildExecutable(TestCommon):

    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_create_parser(self):
        # test the argument parsing
        parser = create_parser()
        sys.argv = ["", "package", "--solution", "1234", "--output_path", "An_example_path"]
        args = parser.parse_known_args()
        self.assertEqual("1234", args[0].solution)
        self.assertEqual("An_example_path", args[0].output_path)
        self.assertEqual(inspect.getsource(album_package), inspect.getsource(args[0].func))

        sys.argv = ["", "package", "--output_path", "An_example_path"]
        args = parser.parse_known_args()
        self.assertEqual(None, args[0].solution)
        self.assertEqual("An_example_path", args[0].output_path)
        self.assertEqual(inspect.getsource(album_package), inspect.getsource(args[0].func))

    def test_fill_placeholder(self):
        # prepare
        output_path = Path(self.tmp_dir.name)
        solution = pkg_resources.resource_filename('test_package.resources.test_solution', 'solution.py')
        solution_double_backslash = re.sub(r'\\', r'\\\\', solution)
        coordinates = "album:import_unittest:0.1.0"
        test_str = "%s\n%s" % (solution_double_backslash, coordinates)

        # call
        fill_placeholder(output_path, solution, coordinates)

        with open(Path(output_path).joinpath('solution_info.txt'), 'r') as file:
            solution_info = file.read()

        # assert
        self.assertEqual(test_str, solution_info)

    def test_create_parameter(self):
        # prepare
        ns = Namespace(
            solution=pkg_resources.resource_filename('test_package.resources.test_solution', 'solution.py'),
            output_path=self.tmp_dir.name)
        install_mamba_script = pkg_resources.resource_filename('album.package', 'install_mamba.py')
        solution_info_path = str(Path(self.tmp_dir.name).joinpath('solution_info.txt'))
        pyinstaller_params = [str(pkg_resources.resource_filename('album.package', 'install_all.py')),
                              '--onefile', '--name=album_installer', '--distpath=%s' % str(self.tmp_dir.name),
                              '--add-data=%s%s%s' % (install_mamba_script, os.pathsep, '.'),
                              '--add-data=%s%s%s' % (solution_info_path, os.pathsep, '.'),
                              '--workpath=%s' % str(Path(self.tmp_dir.name).joinpath('build')),
                              '--specpath=%s' % str(self.tmp_dir.name), '--log-level=ERROR',
                              "--hidden-import=pkg_resources"]

        # call
        script_pyinstaller_params = create_pyinstaller_params(ns, '--name=album_installer')

        # assert
        self.assertEqual(pyinstaller_params, script_pyinstaller_params)


if __name__ == '__main__':
    unittest.main()
