from album.executable import build_executable


def create_executable_parser(parser):
    p = parser.create_command_parser('package', build_executable.run, 'Build an executable which runs the solution.')
    p.add_argument('solution', type=str, help='path of the solution file')
    p.add_argument('--output_path', type=str, required=True,
                   help='Path where the executable solution should be written to.')
    p.add_argument('--no_gui', required=False, default=False,
                   help='Should the solution not be launched in the album gui when executed?', action="store_true")
