# Album plugin for packaging solutions into executables

This plugin is used to create installation executables for Album and Album solutions, so Album and a solution can be
installed with a simple double click. The executable creates a shortcut for running Albums UI on the desktop of the
user. The executables can be distributed to a different system running the same operating system on the same CPU
architecture. To create executables for different operating systems or CPU architectures, run this plugin on a system
running the target operating system and architecture. For example, the CI of this repository builds separate macOS
installers for Apple silicon (arm64) and Intel (x86_64) Macs. If the target system runs Windows or MacOS it doesn't
need to have anything preinstalled, the executable will install every needed component (Micromamba and album) into the
~/.album directory if they are not already installed in this location. Linux users need to have the binutils package
installed.

## Installation:

1. [Install Album](https://docs.album.solutions/en/latest/installation-instructions.html#)
2. Activate the album environment:

```
micromamba activate album
```

3. Install the album package plugin:

```
micromamba install album-package -c conda-forge
```

Or via pip:

```
pip install album-package
```

4. If you are using a linux system, make sure the source and the target system got the binutils package installed. For
   example on ubuntu it can be installed with the following command:

```
apt-get update && apt-get install binutils
```

## Usage:

To create an executable which installs Album run following command:

```
album package --output_path /your/output/path
```

To create an executable which installs Album and a solution in one go run following command:

```
album package --solution /path/to/your/solution.py --output_path /your/output/path
```

Instead of a path you can also pass the coordinates of a solution available in one of your catalogs:

```
album package --solution group:name:version --output_path /your/output/path
```

If several of your catalogs contain a solution with these coordinates, album takes it from the first one. Prefix the
coordinates with the name of the catalog to package the solution of a specific catalog:

```
album package --solution catalog:group:name:version --output_path /your/output/path
```

The solution is contained in the executable, the target system does not need access to the solution on the system the
executable was built on. When the executable runs, it copies the solution to
`~/.album/packaged_solutions/<group>_<name>_<version>/` and installs it from there with `album install`. album copies
the installed solution into its collection, so the copy is removed after a successful installation. If the
installation of the solution fails, the executable prints the error and exits with a non-zero exit code; the copy is
kept, so you can install it manually with `album install <path of the copy>`.

album treats the bundled solution like any solution installed from a local path, also if you packaged it by its
coordinates: on the target system it is added to album's local cache catalog, not to the catalog it came from, so
updates of that catalog do not apply to it. Parent solutions are not packaged, album resolves them from the catalogs
of the target system during the installation.


### Input parameter:

- solution: The album solution which should be packed into an executable. If you provide the path to a directory
  containing a solution.py all files in the directory will be packaged into the solution executable. If you provide
  the direct path to a solution.py only the solution will packaged. If your solution contains local imports, make sure
  all imported files lie in the same directory as the solution and you provide the path containing the solution.py.
  You can also provide the coordinates (group:name:version or catalog:group:name:version) of a solution, in this case
  album resolves the solution and all files in the directory of the resolved solution will be packaged. For other
  inputs album can resolve (e.g. a URL or a DOI), all files next to the resolved solution.py are packaged (zip file,
  DOI) or, for the URL of a single solution file, only the downloaded file. If this parameter is not set, the
  resulting executable will only install Album without a solution.
- output_path: The path where the executable should be saved. Missing parent directories are created. If you package a
  solution directory (or coordinates), the output path must not be that directory itself; if it lies inside the
  solution directory, it is not packaged into the executable. If you package a single solution file, the output path
  can be the directory of the file.
