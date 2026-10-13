from album.api import Album


def album_package(album_instance: Album, args):
    from album.package.build_executable import run
    run(album_instance, args)


def create_executable_parser(parser):
    p = parser.create_command_parser('package', album_package, 'Build an package which installs the solution.')
    p.add_argument('--solution', type=str,
                   help='The solution which gets bundled into the installer. Either the path to a solution file '
                        'or to a directory containing a solution.py, or the coordinates (group:name:version or '
                        'catalog:group:name:version) of a solution in your album collection. If not set, the '
                        'installer only installs album.')
    p.add_argument('--output_path', type=str, required=True, help='Path where the package solution should be written to.')
