# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['call_solution_gui.py'],
			 pathex=[],
			 binaries=[],
			 datas=[(<yml_path>, '.'),(<solution_path>, 'solution_files'),(<run_sol_path>, '.'),(<uninstall_sol_path>, '.'),(<icon>, '.')],
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
          a.binaries,
          a.zipfiles,
          a.datas,
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
