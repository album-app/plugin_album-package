import os
import shutil
import tempfile
import unittest
from argparse import Namespace
from importlib.resources import files
from pathlib import Path
from unittest import mock

from album.api import Album
from album.core.utils.operations.file_operations import force_remove

from album.package import build_executable


class TestIntegrationPackageCoordinates(unittest.TestCase):
    """Packages a solution by its coordinates, resolved by a real album instance.

    The same solution (album:import-unittest:0.1.0) is deployed to two local catalogs, each copy marked with the name
    of its catalog, so the tests can tell which copy got bundled. PyInstaller is not run, the tests check the files
    and the coordinates which would be bundled into the executable.
    """

    CATALOGS = ["package_test_catalog_one", "package_test_catalog_two"]
    COORDINATES = "album:import-unittest:0.1.0"

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp_dir = tempfile.mkdtemp()
        cls.album = Album.Builder().base_cache_path(Path(cls.tmp_dir).joinpath("album")).build()
        cls.album.load_or_create_collection()
        solution = files("test_package.resources.test_solution").joinpath("solution.py")
        for catalog in cls.CATALOGS:
            solution_dir = Path(cls.tmp_dir).joinpath("solution_%s" % catalog)
            solution_dir.mkdir()
            shutil.copy(str(solution), solution_dir.joinpath("solution.py"))
            with open(solution_dir.joinpath("solution.py"), "a") as file:
                file.write("\n# deployed to %s\n" % catalog)
            catalog_path = str(Path(cls.tmp_dir).joinpath(catalog))
            cls.album.clone("template:catalog", catalog_path, catalog)
            cls.album.add_catalog(catalog_path)
            cls.album.deploy(str(solution_dir), catalog, dry_run=False, git_email="album@example.com",
                             git_name="album-package tests", no_conda_lock=True)
            cls.album.update(catalog)
            cls.album.upgrade(catalog)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.album.close()
        force_remove(cls.tmp_dir)

    def package(self, solution):
        """Runs `album package --solution <solution>` and returns the bundled solution.py and solution_info.txt."""
        output_path = Path(self.tmp_dir).joinpath("output", solution.replace(":", "_"))
        bundled = {}

        def pyinstaller(params):
            bundle = [param[len("--add-data="):].rsplit(os.pathsep, 1)[0] for param in params
                      if param.startswith("--add-data=") and param.endswith(os.pathsep + build_executable.SOLUTION_BUNDLE_DIR)]
            self.assertEqual(1, len(bundle), "Expected exactly one bundled solution in %s" % params)
            bundled["solution"] = Path(bundle[0]).joinpath("solution.py").read_text()
            bundled["info"] = output_path.joinpath("solution_info.txt").read_text()
            bundled["name"] = [param for param in params if param.startswith("--name=")]

        with mock.patch.object(build_executable.PyInstaller.__main__, "run", side_effect=pyinstaller):
            build_executable.run(self.album, Namespace(solution=solution, output_path=str(output_path)))
        return bundled

    def assert_packaged(self, bundled, catalog):
        self.assertTrue(bundled["solution"].rstrip().endswith("# deployed to %s" % catalog),
                        "Expected the solution of catalog %s to be bundled." % catalog)
        self.assertTrue(bundled["info"].rstrip().endswith(self.COORDINATES))
        self.assertEqual(1, len(bundled["name"]))
        self.assertTrue(bundled["name"][0].startswith("--name=album_import-unittest_0_1_0_installer"))

    def test_group_name_version(self):
        # without a catalog album takes the solution from the first catalog containing it
        self.assert_packaged(self.package(self.COORDINATES), self.CATALOGS[0])

    def test_catalog_group_name_version(self):
        for catalog in self.CATALOGS:
            with self.subTest(catalog=catalog):
                self.assert_packaged(self.package("%s:%s" % (catalog, self.COORDINATES)), catalog)

    def test_unknown_catalog(self):
        with self.assertRaises(RuntimeError):
            self.package("package_test_catalog_unknown:%s" % self.COORDINATES)


if __name__ == "__main__":
    unittest.main()
