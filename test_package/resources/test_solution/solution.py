from album.runner.api import setup, get_args

env_file = """name: import_unittest
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.9
  - pip
"""

def install():
    from album.runner.api import setup, get_args , get_package_path

def run():
    from album.runner.api import setup, get_args , get_package_path
    from pathlib import Path
    import sys
    import os
    import subprocess
    from meintest import a
    print(a)
    print('Hallo ich bin eine als package ausgeführte Solution!!!')
    print("Success!")

def test():
    from album.runner.api import setup, get_args
    print("Hallo")

def close():
    from album.runner.api import setup, get_args
    print("closing")

setup(
    group="album",
    name="import_unittest",
    version="0.1.0",
    title="A Solution the unittest of the album package plugin",
    description="A Solution to run the Vascuec App.",
    authors=["Lucas Rieckert", "Jan Philipp Albrecht"],
    cite=[{
        "text": "Your first citation text",
        "doi": "your first citation doi"
    }],
    tags=["unittest"],
    license="UNLICENSE",
    documentation="",
    covers=[{
        "description": "Dummy cover image.",
        "source": "cover.png"
    }],
    album_api_version="0.4.2",
    install=install,
    run=run,
    close=close,
    test=test,
    dependencies={'environment_file': env_file}
)
