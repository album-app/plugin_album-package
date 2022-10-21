import time
import unittest

from test_package.unit import test_unit_build_executable
from test_package.unit import test_unit_install_all
from test_package.unit import test_unit_install_mamba


def main():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromModule(test_unit_build_executable))
    suite.addTests(loader.loadTestsFromModule(test_unit_install_all))
    suite.addTests(loader.loadTestsFromModule(test_unit_install_mamba))

    runner = unittest.TextTestRunner(verbosity=3)
    result = runner.run(suite)
    if result.wasSuccessful():
        time.sleep(5)
        print("Success")
        exit(0)
    else:
        print("Failed")
        exit(1)


main()
