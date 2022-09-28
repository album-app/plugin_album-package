import gc
import sys
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from album.api import Album
from album.core.api.model.collection_solution import ICollectionSolution
from album.core.utils.operations.file_operations import force_remove
from album.runner.core.model.coordinates import Coordinates


class TestCommon(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.setup_tmp_resources()
        self.album_mock = mock.create_autospec(Album)
        self.resolve_result = mock.create_autospec(ICollectionSolution)
        self.album_mock.resolve.return_value = self.resolve_result
        self.resolve_result.coordinates.return_value = Coordinates("album", "import_unittest", "0.1.0")

    def tearDown(self) -> None:
        if self.album_mock:
            self.album_mock.close()
        self.teardown_tmp_resources()
        super().tearDown()

    def setup_tmp_resources(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.album_dir = Path(self.tmp_dir.name).joinpath('.album')
        self.mamba_dir = Path(self.tmp_dir.name).joinpath('micromamba')
        self.desktop_dir = Path(self.tmp_dir.name).joinpath('Desktop')
        Path(self.album_dir).mkdir()
        Path(self.mamba_dir).mkdir()
        Path(self.desktop_dir).mkdir()
        self.closed_tmp_file = tempfile.NamedTemporaryFile(delete=False)
        self.closed_tmp_file.close()
        #os.chmod(self.closed_tmp_file.name, 0o777)

    def teardown_tmp_resources(self):
        # garbage collector
        gc.collect()

        try:
            Path(self.closed_tmp_file.name).unlink()
            self.tmp_dir.cleanup()
        except PermissionError:
            try:
                force_remove(self.tmp_dir.name)
            except PermissionError:
                if sys.platform == 'win32' or sys.platform == 'cygwin':
                    pass
                else:
                    raise
