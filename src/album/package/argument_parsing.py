from album.api import Album


def album_package(album_instance: Album, args):
    from album.package.build_executable import run
    run(album_instance, args)


def create_executable_parser(parser):
    p = parser.create_command_parser('package', album_package, 'Build an package which runs the solution.')
    p.add_argument('solution', type=str, help='path of the solution file')
    p.add_argument('output_path', type=str, help='Path where the package solution should be written to.')
    p.add_argument('--no_gui', required=False, default=False,
                   help='Should the solution not be launched in the album gui when executed?', action="store_true")
