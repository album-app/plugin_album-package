# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

We use the following:

- `Added` for new features.
- `Changed` for changes in existing functionality.
- `Deprecated` for soon-to-be removed features.
- `Removed` for now removed features.
- `Fixed` for any bug fixes.
- `Security` in case of vulnerabilities.

## [unreleased]

### Added

- Solution installers contain the solution now: `album package --solution` bundles the solution directory, the single
  solution file or, for coordinates (`group:name:version`) and other inputs resolved by album, the directory of the
  resolved `solution.py` (only the downloaded file for the URL of a single solution file) into the executable. The
  installer copies it to `~/.album/packaged_solutions/<group>_<name>_<version>/` and installs it from there. The copy
  is removed after a successful installation and kept if the installation fails.

### Changed

- The installer prints an error (including the last lines of the output of `album install` / `micromamba install`) and
  exits with a non-zero exit code if installing the solution or album gui fails, instead of printing
  "Installation successfully finished." Failing micromamba / album calls, download errors and unsupported systems
  are reported as `ERROR: ...` without a Python traceback.
- `--output_path` is created including missing parent directories
- `--output_path` must not be the solution directory itself if a solution directory or coordinates are packaged (the
  build fails with an error); an output path inside the solution directory is not packaged into the executable
- `--solution` help text and README: coordinates are accepted, installers are specific to the operating system and the
  CPU architecture
- `--solution` help text and README: `catalog:group:name:version` packages the solution of a specific catalog (with
  `group:name:version` album takes the first catalog containing the solution), covered by integration tests
- Installers do not contain `cryptography` anymore, the installer never uses it
- Python 3.14 is listed among the supported Python versions; the CI tests it

### Removed

- The installers do not run `micromamba shell init` anymore and leave `~/.bashrc`, `~/.zshrc` and the PowerShell
  profile unchanged, so an existing conda / micromamba setup of the shell keeps working. With micromamba 2.x the call
  failed unnoticed anyway (`shell init` has no `-p` option anymore). The installer, album and the Album shortcut call
  micromamba by its absolute path; the Album documentation shows how to activate `~/.album/envs/album` on the command
  line

### Fixed

- Installers built on Linux with album-package from conda-forge stopped right away with "Can't connect to HTTPS URL
  because the SSL module is not available": conda-forge's `cryptography` made PyInstaller bundle the system's
  `libcrypto` next to the environment's `libssl`. A CI job (started manually) builds and runs the installer with the
  dependencies from conda-forge
- Solution installers only contained the absolute path of the solution on the build machine and could not install the
  solution on any other machine
- The check for an existing album / album gui installation always failed (`bytes` stderr compared with `""`), so every
  solution installer ran the full installation (`micromamba create` on the existing `~/.album/envs/album`
  environment)
- Installing a missing album gui in development mode (`ALBUM_DEV_PACKAGE_CONSTRAINTS` set): broken micromamba arguments
  (`"run -p"`, `"install --yes"` passed as single arguments)
- Micromamba download on Linux arm64 and ppc64le (`uname -m` reports `aarch64` / `ppc64le`)
- Building with a relative `--output_path` (PyInstaller could not find `solution_info.txt`)

## [0.5.1]

### Changed

- pyproject.toml over setup.cfg
- Changelog to repository 
- Removed conda support — micromamba is now the only supported package manager
- Removed conda-specific integration test files


[unreleased]: https://gitlab.com/album-app/album-package/-/compare/v0.5.1...HEAD
[0.5.1]: https://gitlab.com/album-app/album-package/-/compare/v0.5.0...v0.5.1
[0.5.0]: https://gitlab.com/album-app/album-package/-/compare/v0.4.2...v0.5.0
[0.4.2]: https://gitlab.com/album-app/album-package/-/compare/v0.4.1...v0.4.2
[0.4.1]: https://gitlab.com/album-app/album-package/-/compare/v0.4.0...v0.4.1
[0.4.0]: https://gitlab.com/album-app/album-package/-/compare/v0.3.3...v0.4.0
[0.3.3]: https://gitlab.com/album-app/album-package/-/compare/v0.3.2...v0.3.3
[0.3.2]: https://gitlab.com/album-app/album-package/-/compare/v0.3.1...v0.3.2
[0.3.1]: https://gitlab.com/album-app/album-package/-/compare/v0.3.0...v0.3.1
[0.3.0]: https://gitlab.com/album-app/album-package/-/compare/v0.2.1...v0.3.0
[0.2.1]: https://gitlab.com/album-app/album-package/-/compare/v0.2.0...v0.2.1
[0.2.0]: https://gitlab.com/album-app/album-package/-/tags/v0.2.0
