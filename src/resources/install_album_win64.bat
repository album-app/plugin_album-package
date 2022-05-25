@echo off

setlocal enableDelayedExpansion

set TARGET=%userprofile%\.album
set BRANCH=main
set ALBUM_PIP_VERSION=https://gitlab.com/album-app/album/-/archive/%BRANCH%/album-%BRANCH%.zip
echo Installing album (branch %BRANCH%) into %TARGET%..

if not exist "%TARGET%" mkdir %TARGET%

echo Creating installation script %POWERSHELL_SCRIPT%
set POWERSHELL_SCRIPT=%TARGET%\install-album.ps1
echo. >NUL 2>%POWERSHELL_SCRIPT%
(
    echo $ErrorActionPreference = "Stop"
    echo.
    echo $BASE_PATH = "$HOME\.album"
    echo echo "Base path: $BASE_PATH"
    echo $MINICONDA_URL = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
    echo echo "Miniconda download URL: $MINICONDA_URL"
    echo $MINICONDA_PATH = "$HOME\miniconda3"
    echo echo "Miniconda path: $MINICONDA_PATH"
    echo $MINICONDA_INSTALL_SCRIPT_PATH = "$MINICONDA_PATH\miniconda.exe"
    echo $CONDA_EXECUTABLE = "$MINICONDA_PATH\bin\conda"
    echo $ALBUM_ENV_PATH = "$BASE_PATH\env\album"
    echo $COLLECTION_BASE_PATH = "$BASE_PATH\collection\"
    echo $ALBUM_ACTIVATION = "$BASE_PATH\activate.bat"
    echo $ALBUM_DEACTIVATION = "$BASE_PATH\deactivate.bat"
    echo $ALBUM_GUI_URL = "https://gitlab.com/album-app/plugins/album-gui/-/archive/main/album-gui-main.zip"
    echo $remove_existing = $FALSE
    echo $oldProgressPreference = $progressPreference; $progressPreference = 'SilentlyContinue';
    echo if^(Test-Path $BASE_PATH^) ^{
    echo   echo "$BASE_PATH already exists."
    echo ^} else^{
    echo   mkdir $BASE_PATH
    echo ^}
    echo try^{
    echo   $CONDA_FOUND = $true
    echo   conda info
    echo ^}
    echo catch^{
    echo   echo "No conda found. Downloading miniconda installer.."
    echo   $CONDA_FOUND = $false
    echo   mkdir $MINICONDA_PATH
    echo   [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    echo   Invoke-WebRequest -UseBasicParsing -Uri $MINICONDA_URL -OutFile $MINICONDA_INSTALL_SCRIPT_PATH
    echo ^}
    echo finally^{
    echo   if^( $CONDA_FOUND ^) ^{
    echo      $CONDA_STR = conda info
    echo      $CONDA_SUB_STR_UNTRIMMED = $CONDA_STR -match "base environment"
    echo      $CONDA_SUB_STR_TRIMMED_1 = $CONDA_SUB_STR_UNTRIMMED.Substring^("26"^)
    echo      $CONDA_SUB_STR_TRIMMED_2 = $CONDA_SUB_STR_TRIMMED_1.TrimEnd^(" (writable)"^)
    echo      $MINICONDA_PATH = $CONDA_SUB_STR_TRIMMED_2
    echo      echo "Found Conda Installation at: $MINICONDA_PATH"
    echo   ^}
    echo ^}
    echo $env:PATH += ";$MINICONDA_PATH\condabin"
    echo if^(Test-Path $MINICONDA_PATH\condabin^) ^{
    echo 	echo "Conda command already available..."
    echo ^} else ^{
    echo 	echo "Will install conda into $MINICONDA_PATH..."
    echo 	Start-Process $MINICONDA_INSTALL_SCRIPT_PATH -argumentlist "/InstallationType=JustMe /S /D=$MINICONDA_PATH" -wait
    echo ^}
    echo $conda = "$MINICONDA_PATH\condabin\conda"
    echo $install_env = $remove_existing
    echo if^(Test-Path $ALBUM_ENV_PATH^) ^{
    echo   if^($remove_existing^) ^{
    echo     echo "Removing already existing album environment.."
    echo     # ^& $conda  remove -q -y --prefix $ALBUM_ENV_PATH --all
    echo     rm -r -fo $ALBUM_ENV_PATH
    echo   ^} else ^{
    echo     echo "Environment album already exists.."
    echo   ^}
    echo ^} else ^{
    echo   $install_env = $TRUE
    echo ^}
    echo $env:PATH ^+= ";$MINICONDA_PATH"
    echo $env:PATH ^+= ";$MINICONDA_PATH\condabin"
    echo $env:PATH ^+= ";$MINICONDA_PATH\Scripts\"
    echo $env:PATH ^+= ";$MINICONDA_PATH\Library\bin"
    echo ^& $conda install -c conda-forge mamba
    echo if^($install_env^) ^{
    echo   echo "Installing album environment.."
    echo   ^& $conda create -c defaults -c conda-forge -y --prefix $ALBUM_ENV_PATH python=3.9 pip git=2.34
    echo ^}
    echo ^& $conda env config vars set ALBUM_BASE_CACHE_PATH=$COLLECTION_BASE_PATH --prefix $ALBUM_ENV_PATH
    echo ^& $conda deactivate
	echo $PYTHON="$ALBUM_ENV_PATH\python"
    echo echo "Activating album environment.."
    echo ^& "$MINICONDA_PATH\condabin\activate" $ALBUM_ENV_PATH
    echo echo "Installing album into environment.."
    echo ^& $PYTHON -m pip uninstall -y -q album
    echo ^& $PYTHON -m pip install --trusted-host=pypi.python.org --trusted-host=pypi.org --trusted-host=files.pythonhosted.org --trusted-host=gitlab.com %ALBUM_PIP_VERSION%
    echo ^& $conda run -p $ALBUM_ENV_PATH pip install $ALBUM_GUI_URL
    echo ^& "$MINICONDA_PATH\condabin\deactivate"
) >%POWERSHELL_SCRIPT%
Powershell.exe -executionpolicy remotesigned -File %POWERSHELL_SCRIPT%
del %POWERSHELL_SCRIPT%