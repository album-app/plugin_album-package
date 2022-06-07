import os
import platform
from pathlib import Path


# res_path is needed since when this function is called from the unit tests on a remote runner the paths where the file
# live can be different

def run(output_path, solution, res_path):
    install_script_path = ""
    if not res_path:
        if platform.system() == 'Windows':
            install_script_path = Path(os.path.realpath(__file__)).parent.parent.parent.joinpath('resources',
                                                                                                 'install_album_win64.bat')
        elif platform.system() == 'Linux':
            install_script_path = Path(os.path.realpath(__file__)).parent.parent.parent.joinpath('resources',
                                                                                                 'install_album_linux64.sh')
        elif platform.system() == 'Darwin':
            install_script_path = Path(os.path.realpath(__file__)).parent.parent.parent.joinpath('resources',
                                                                                                 'install_album_macos.sh')
    else:
        if platform.system() == 'Windows':
            install_script_path = Path(res_path).joinpath('install_album_win64.bat')
        elif platform.system() == 'Linux':
            install_script_path = Path(res_path).joinpath('install_album_linux64.sh')
        elif platform.system() == 'Darwin':
            install_script_path = Path(res_path).joinpath('install_album_macos.sh')

    spec_path = Path(output_path).joinpath('build_executable_gui.spec')

    file = open(spec_path, "w")
    file.write('# -*- mode: python ; coding: utf-8 -*-\n\n\n')
    file.write('block_cipher = None\n\n\n')
    file.write('a = Analysis([\'execute_solution_gui.py\'],\n')
    file.write('\t\t\t pathex=[],\n')
    file.write('\t\t\t binaries=[],\n')
    file.write('\t\t\t datas=[(')
    file.write(repr(str(install_script_path)))
    file.write(', \'.\'),')
    file.write('(')
    file.write(repr(str(Path(solution).parent.joinpath('*'))))
    file.write(', \'solution_files\')],\n')
    file.write('\t\t\t hiddenimports=[\'pkg_resources\'],\n')
    file.write('\t\t\t hookspath=[],\n')
    file.write('\t\t\t hooksconfig={},\n')
    file.write('\t\t\t runtime_hooks=[')
    file.write(repr(str(Path(output_path).joinpath('install_hook.py'))))
    file.write('],\n')
    file.write('\t\t\t excludes=[],\n')
    file.write('\t\t\t win_no_prefer_redirects=False,\n')
    file.write('\t\t\t win_private_assemblies=False,\n')
    file.write('\t\t\t cipher=block_cipher,\n')
    file.write('\t\t\t noarchive=False)\n')
    file.write('pyz = PYZ(a.pure, a.zipped_data,\n')
    file.write('\t\t\t cipher=block_cipher)\n\n')
    file.write('exe = EXE(pyz,\n')
    file.write('\t\t  a.scripts,\n')
    file.write('\t\t  [],\n')
    file.write('\t\t  exclude_binaries=True,\n')
    file.write('\t\t  name=\'solution\',\n')
    file.write('\t\t  debug=False,\n')
    file.write('\t\t  bootloader_ignore_signals=False,\n')
    file.write('\t\t  strip=False,\n')
    file.write('\t\t  upx=True,\n')
    file.write('\t\t  console=True,\n')
    file.write('\t\t  disable_windowed_traceback=False,\n')
    file.write('\t\t  target_arch=None,\n')
    file.write('\t\t  codesign_identity=None,\n')
    file.write('\t\t  entitlements_file=None )\n')
    file.write('coll = COLLECT(exe,\n')
    file.write('\t\t\t   a.binaries,\n')
    file.write('\t\t\t   a.zipfiles,\n')
    file.write('\t\t\t   a.datas,\n')
    file.write('\t\t\t   strip=False,\n')
    file.write('\t\t\t   upx=True,\n')
    file.write('\t\t\t   upx_exclude=[],\n')
    file.write('\t\t\t   name=\'solution\')\n')
    file.close()

    return spec_path
