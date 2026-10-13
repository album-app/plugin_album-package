import inspect
import os
import re
import sys
import unittest.mock
from argparse import Namespace
from importlib.resources import files
from pathlib import Path

from album.argument_parsing import create_parser
from album.package import build_executable
from album.package.argument_parsing import album_package
from album.package.build_executable import fill_placeholder, create_pyinstaller_params, get_solution_files, \
    prepare_solution_bundle, SOLUTION_BUNDLE_DIR
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
        solution = str(files('test_package.resources.test_solution').joinpath('solution.py'))
        solution_double_backslash = re.sub(r'\\', r'\\\\', solution)
        coordinates = "album:import-unittest:0.1.0"
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
            solution=str(files('test_package.resources.test_solution').joinpath('solution.py')),
            output_path=self.tmp_dir.name)
        install_mamba_script = str(files('album.package').joinpath('install_mamba.py'))
        solution_info_path = str(Path(self.tmp_dir.name).joinpath('solution_info.txt'))
        pyinstaller_params = [str(files('album.package').joinpath('install_all.py')),
                              '--onefile', '--name=album_installer', '--distpath=%s' % str(self.tmp_dir.name),
                              '--add-data=%s%s%s' % (install_mamba_script, os.pathsep, '.'),
                              '--add-data=%s%s%s' % (solution_info_path, os.pathsep, '.'),
                              '--workpath=%s' % str(Path(self.tmp_dir.name).joinpath('build')),
                              '--specpath=%s' % str(self.tmp_dir.name), '--log-level=ERROR']

        # call
        script_pyinstaller_params = create_pyinstaller_params(ns, '--name=album_installer')

        # assert
        self.assertEqual(pyinstaller_params, script_pyinstaller_params)

    def test_create_parameter_relative_output_path(self):
        # prepare
        ns = Namespace(solution=None, output_path='relative_output')
        # PyInstaller resolves relative data paths relative to the spec path (which is the output path)
        solution_info_path = str(Path('relative_output').absolute().joinpath('solution_info.txt'))

        # call
        script_pyinstaller_params = create_pyinstaller_params(ns, '--name=album_installer')

        # assert
        self.assertIn('--add-data=%s%s%s' % (solution_info_path, os.pathsep, '.'), script_pyinstaller_params)

    def test_create_parameter_solution_bundle(self):
        # prepare
        ns = Namespace(solution=None, output_path=self.tmp_dir.name)
        solution_bundle = Path(self.tmp_dir.name).joinpath('build', 'solution_bundle')

        # call
        script_pyinstaller_params = create_pyinstaller_params(ns, '--name=album_installer', solution_bundle)

        # assert
        self.assertEqual(create_pyinstaller_params(ns, '--name=album_installer'), script_pyinstaller_params[:-1])
        self.assertEqual('--add-data=%s%s%s' % (solution_bundle, os.pathsep, 'solution'), script_pyinstaller_params[-1])

    def _create_solution_dir(self, *path):
        solution_dir = Path(self.tmp_dir.name).joinpath(*path)
        solution_dir.joinpath('data').mkdir(parents=True)
        solution_dir.joinpath('solution.py').write_text('# solution')
        solution_dir.joinpath('data', 'model.txt').write_text('model')
        return solution_dir

    def test_get_solution_files(self):
        # prepare
        solution_dir = self._create_solution_dir('my_solution')
        catalog_solution_dir = self._create_solution_dir('catalog', 'solutions', 'album', 'import-unittest', '0.1.0')
        self.resolve_result.path.return_value = catalog_solution_dir.joinpath('solution.py')

        # call and assert
        self.assertEqual(solution_dir, get_solution_files(str(solution_dir), self.resolve_result))
        self.assertEqual(solution_dir.joinpath('solution.py'),
                         get_solution_files(str(solution_dir.joinpath('solution.py')), self.resolve_result))
        # coordinates are resolved by album, the directory of the resolved solution gets bundled
        self.assertEqual(catalog_solution_dir, get_solution_files('album:import-unittest:0.1.0', self.resolve_result))

    def test_get_solution_files_downloaded_file(self):
        # prepare: album stores a solution file downloaded from a URL as a temporary file without a .py suffix next
        # to all its other downloads
        downloads_dir = Path(self.tmp_dir.name).joinpath('album', 'downloads')
        self._create_solution_dir('album', 'downloads', 'tmp_extracted_zip')
        downloads_dir.joinpath('tmp_other_download').write_text('# another download')
        downloaded_file = downloads_dir.joinpath('tmpabc')
        downloaded_file.write_text('# solution')
        self.resolve_result.path.return_value = downloaded_file

        # call and assert: only the downloaded file gets bundled, not the whole download cache of album
        self.assertEqual(downloaded_file, get_solution_files('https://host/solution.py', self.resolve_result))

    def test_get_solution_files_downloaded_zip(self):
        # prepare: a zip file or DOI downloaded by album gets extracted into its own folder
        extracted_dir = self._create_solution_dir('album', 'downloads', 'tmp_extracted_zip')
        self.resolve_result.path.return_value = extracted_dir.joinpath('solution.py')

        # call and assert
        self.assertEqual(extracted_dir, get_solution_files('https://host/solution.zip', self.resolve_result))

    def test_prepare_solution_bundle_file(self):
        # prepare
        solution_file = self._create_solution_dir('my_solution').joinpath('solution.py')
        output_path = Path(self.tmp_dir.name).joinpath('output')

        # call
        solution_bundle, bundled_solution = prepare_solution_bundle(solution_file, output_path)

        # assert
        self.assertEqual(solution_file, solution_bundle)
        self.assertEqual('solution/solution.py', bundled_solution)

    def test_prepare_solution_bundle_dir(self):
        # prepare
        solution_dir = self._create_solution_dir('my_solution')
        output_path = Path(self.tmp_dir.name).joinpath('output')

        # call
        solution_bundle, bundled_solution = prepare_solution_bundle(solution_dir, output_path)

        # assert
        self.assertEqual(SOLUTION_BUNDLE_DIR, bundled_solution)
        self.assertEqual(output_path.resolve().joinpath('build', 'solution_bundle'), solution_bundle)
        self.assertEqual('# solution', solution_bundle.joinpath('solution.py').read_text())
        self.assertEqual('model', solution_bundle.joinpath('data', 'model.txt').read_text())

    def test_prepare_solution_bundle_output_path_inside_solution_dir(self):
        # prepare
        solution_dir = self._create_solution_dir('my_solution')
        output_path = solution_dir.joinpath('installer')
        output_path.mkdir()
        output_path.joinpath('old_installer').write_text('old installer')

        # call
        solution_bundle, bundled_solution = prepare_solution_bundle(solution_dir, output_path)

        # assert
        self.assertTrue(solution_bundle.joinpath('solution.py').is_file())
        self.assertTrue(solution_bundle.joinpath('data', 'model.txt').is_file())
        self.assertFalse(solution_bundle.joinpath('installer').exists(), 'The output path must not be bundled.')

    def test_prepare_solution_bundle_output_path_is_solution_dir(self):
        # prepare
        solution_dir = self._create_solution_dir('my_solution')

        # call and assert
        with self.assertRaises(RuntimeError) as context:
            prepare_solution_bundle(solution_dir, solution_dir)
        self.assertIn('must not be the solution directory', str(context.exception))

    def test_prepare_solution_bundle_file_output_path_is_solution_dir(self):
        # prepare: a single solution file is bundled as it is, the output path may be its directory
        solution_dir = self._create_solution_dir('my_solution')

        # call
        solution_bundle, bundled_solution = prepare_solution_bundle(solution_dir.joinpath('solution.py'), solution_dir)

        # assert
        self.assertEqual(solution_dir.joinpath('solution.py'), solution_bundle)
        self.assertEqual('solution/solution.py', bundled_solution)

    def test_run_output_path_is_solution_dir(self):
        # prepare
        solution_dir = self._create_solution_dir('my_solution')

        # call and assert
        with unittest.mock.patch('album.package.build_executable.PyInstaller.__main__.run') as pyinstaller_run:
            with self.assertRaises(RuntimeError) as context:
                build_executable.run(self.album_mock, Namespace(solution=str(solution_dir), output_path=solution_dir))
        pyinstaller_run.assert_not_called()
        self.assertIn('must not be the solution directory', str(context.exception))
        self.assertNotIn('..', str(context.exception))
        self.assertTrue(solution_dir.joinpath('solution.py').is_file())
        self.assertFalse(solution_dir.joinpath('build').exists(), 'The build directory was not cleaned up.')

    def _run_build(self, solution, output_path):
        """calls build_executable.run with a mocked PyInstaller call and returns the PyInstaller parameters, the content
        of the solution_info.txt and the files of the solution bundle at the time PyInstaller was called"""
        captured = {}

        def pyinstaller_run(params):
            captured['params'] = params
            captured['solution_info'] = Path(output_path).joinpath('solution_info.txt').read_text()
            bundle = [p for p in params if p.startswith('--add-data=') and p.endswith(os.pathsep + 'solution')]
            captured['bundle'] = bundle
            if bundle:
                source = Path(bundle[0][len('--add-data='):-len(os.pathsep + 'solution')])
                captured['bundle_files'] = sorted(
                    f.relative_to(source).as_posix() for f in source.rglob('*') if f.is_file()
                ) if source.is_dir() else [source.name]

        with unittest.mock.patch('album.package.build_executable.PyInstaller.__main__.run',
                                 side_effect=pyinstaller_run):
            build_executable.run(self.album_mock, Namespace(solution=solution, output_path=output_path))
        return captured

    def test_run_solution_dir(self):
        # prepare
        solution_dir = self._create_solution_dir('my_solution')
        output_path = Path(self.tmp_dir.name).joinpath('output')

        # call
        captured = self._run_build(str(solution_dir), output_path)

        # assert
        self.album_mock.resolve.assert_called_once_with(str(solution_dir))
        self.assertEqual(1, len(captured['bundle']))
        self.assertEqual(['data/model.txt', 'solution.py'], captured['bundle_files'])
        self.assertEqual('solution\nalbum:import-unittest:0.1.0', captured['solution_info'])
        self.assertFalse(output_path.joinpath('build').exists(), 'The build directory was not cleaned up.')
        self.assertFalse(output_path.joinpath('solution_info.txt').exists(), 'solution_info.txt was not cleaned up.')

    def test_run_solution_file(self):
        # prepare
        solution_file = self._create_solution_dir('my_solution').joinpath('solution.py')
        output_path = Path(self.tmp_dir.name).joinpath('output')

        # call
        captured = self._run_build(str(solution_file), output_path)

        # assert
        self.album_mock.resolve.assert_called_once_with(str(solution_file))
        self.assertEqual(['--add-data=%s%s%s' % (solution_file, os.pathsep, 'solution')], captured['bundle'])
        self.assertEqual('solution/solution.py\nalbum:import-unittest:0.1.0', captured['solution_info'])

    def test_run_solution_coordinates(self):
        # prepare
        catalog_solution_dir = self._create_solution_dir('catalog', 'solutions', 'album', 'import-unittest', '0.1.0')
        self.resolve_result.path.return_value = catalog_solution_dir.joinpath('solution.py')
        output_path = Path(self.tmp_dir.name).joinpath('output')

        # call
        captured = self._run_build('album:import-unittest:0.1.0', output_path)

        # assert
        self.album_mock.resolve.assert_called_once_with('album:import-unittest:0.1.0')
        self.assertEqual(1, len(captured['bundle']))
        self.assertEqual(['data/model.txt', 'solution.py'], captured['bundle_files'])
        self.assertEqual('solution\nalbum:import-unittest:0.1.0', captured['solution_info'])

    def test_run_solution_url(self):
        # prepare
        downloads_dir = Path(self.tmp_dir.name).joinpath('album', 'downloads')
        downloads_dir.mkdir(parents=True)
        downloads_dir.joinpath('tmp_other_download').write_text('# another download')
        downloaded_file = downloads_dir.joinpath('tmpabc')
        downloaded_file.write_text('# solution')
        self.resolve_result.path.return_value = downloaded_file
        output_path = Path(self.tmp_dir.name).joinpath('output')

        # call
        captured = self._run_build('https://host/solution.py', output_path)

        # assert
        self.assertEqual(['--add-data=%s%s%s' % (downloaded_file, os.pathsep, 'solution')], captured['bundle'])
        self.assertEqual(['tmpabc'], captured['bundle_files'])
        self.assertEqual('solution/tmpabc\nalbum:import-unittest:0.1.0', captured['solution_info'])

    def test_run_album_only(self):
        # prepare
        output_path = Path(self.tmp_dir.name).joinpath('output')

        # call
        captured = self._run_build(None, output_path)

        # assert
        self.album_mock.resolve.assert_not_called()
        self.assertEqual([], captured['bundle'])
        self.assertEqual('None\nNone', captured['solution_info'])

    def test_run_creates_nested_output_path(self):
        # prepare
        output_path = Path(self.tmp_dir.name).joinpath('not', 'existing', 'output')

        # call
        self._run_build(None, output_path)

        # assert
        self.assertTrue(output_path.is_dir(), 'Output directory was not created.')


if __name__ == '__main__':
    unittest.main()
