# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['execute_solution.py'],
			 pathex=[],
			 binaries=[],
			 datas=[(<install_script_path>, '.'),(<run_solution_path>, 'subscripts'),(<test_solution_path>, 'solution_files')],
			 hiddenimports=['pkg_resources'],
			 hookspath=[],
			 hooksconfig={},
			 runtime_hooks=[<hook_path>],
			 excludes=[],
			 win_no_prefer_redirects=False,
			 win_private_assemblies=False,
			 cipher=block_cipher,
			 noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
			 cipher=block_cipher)

exe = EXE(pyz,
		  a.scripts,
		  [],
		  exclude_binaries=True,
		  name='solution',
		  debug=False,
		  bootloader_ignore_signals=False,
		  strip=False,
		  upx=True,
		  console=True,
		  disable_windowed_traceback=False,
		  target_arch=None,
		  codesign_identity=None,
		  entitlements_file=None )
coll = COLLECT(exe,
			   a.binaries,
			   a.zipfiles,
			   a.datas,
			   strip=False,
			   upx=True,
			   upx_exclude=[],
			   name='solution')
