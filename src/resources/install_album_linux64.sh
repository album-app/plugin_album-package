#!/bin/sh

# exit if any command fails
set -e

target=$HOME
branch="main"

BASE_PATH=$target/album
MINICONDA_URL=https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
MINICONDA_PATH=$BASE_PATH/miniconda3
MINICONDA_INSTALL_SCRIPT_PATH=$MINICONDA_PATH/miniconda.sh
CONDA_EXECUTABLE=conda
ALBUM_PIP_VERSION=https://gitlab.com/album-app/album/-/archive/$branch/album-$branch.zip
ALBUM_ENV_PATH=$BASE_PATH/env/album
COLLECTION_BASE_PATH=$(realpath $BASE_PATH)/collection/
ALBUM_LAUNCHER=$BASE_PATH/run-album
ALBUM_ACTIVATE=$BASE_PATH/activate
ALBUM_DEACTIVATE=$BASE_PATH/deactivate
ALBUM_ENV=$BASE_PATH/album.yml

echo "Installing album into the current directory.."
if [ ! -d "$BASE_PATH" ]; then
  mkdir -p "$BASE_PATH"
fi
{
  $CONDA_EXECUTABLE --version
  echo "Found existing conda command..."
} || {
  echo "Did not find conda command, installing conda..."
  if [ ! -d "$MINICONDA_PATH" ]; then
    mkdir -p $MINICONDA_PATH
  fi
  if [ ! -f "$MINICONDA_INSTALL_SCRIPT_PATH" ]; then
    echo "Downloading miniconda installer.."
    wget $MINICONDA_URL --quiet -O $MINICONDA_INSTALL_SCRIPT_PATH
  fi
  CONDA_EXECUTABLE=$MINICONDA_PATH/bin/conda
  if [ ! -f "$CONDA_EXECUTABLE" ]; then
    echo "Installing miniconda.."
    bash $MINICONDA_INSTALL_SCRIPT_PATH -b -u -p $MINICONDA_PATH  > /dev/null
    rm -rf $MINICONDA_INSTALL_SCRIPT_PATH
  fi
  echo "Calling conda init bash.."
  $CONDA_EXECUTABLE init bash
  echo "Preventing conda from printing long directory prefixes when activating environments from directories.."
  $CONDA_EXECUTABLE config --set env_prompt '({name})'
}

if [ -d "$ALBUM_ENV_PATH" ]; then
  echo "Removing existing album environment.."
  $CONDA_EXECUTABLE remove -q -y --prefix $ALBUM_ENV_PATH --all
fi

echo "Writing the album environment file.."
file=$ALBUM_ENV
echo 'name: album' > $file
echo 'channels:' >> $file
echo '  - defaults' >> $file
echo '  - conda-forge' >> $file
echo 'dependencies:' >> $file
echo '  - python=3.9' >> $file
echo '  - git' >> $file
echo '  - pip' >> $file
echo '  - pip:' >> $file
echo "    - $ALBUM_PIP_VERSION" >> $file

echo "Installing album environment.."
$CONDA_EXECUTABLE install -c conda-forge mamba
$CONDA_EXECUTABLE env create -q --prefix $ALBUM_ENV_PATH -f $ALBUM_ENV
$CONDA_EXECUTABLE env config vars set ALBUM_BASE_CACHE_PATH=$COLLECTION_BASE_PATH --prefix $ALBUM_ENV_PATH

rm $ALBUM_ENV

echo "Writing the activation file.."
file=$ALBUM_ACTIVATE
echo '#!/bin/sh' > $file
echo '' >> $file
echo "SCRIPT_PATH=\"\$( cd -- \"\$(dirname \"\$0\")\" >/dev/null 2>&1 ; pwd -P )\"" >> $file
echo 'ALBUM_ENV_PATH=$SCRIPT_PATH/env/album' >> $file
echo "CONDA_BASE=\$($CONDA_EXECUTABLE info --base)" >> $file
echo 'source $CONDA_BASE/bin/activate $ALBUM_ENV_PATH' >> $file
chmod +x $ALBUM_ACTIVATE

echo "Writing the deactivation file.."
file=$ALBUM_DEACTIVATE
echo '#!/bin/sh' > $file
echo '' >> $file
echo "CONDA_BASE=\$($CONDA_EXECUTABLE info --base)" >> $file
echo 'source $CONDA_BASE/bin/deactivate' >> $file
chmod +x $ALBUM_DEACTIVATE

echo "Writing the launcher file.."
file=$ALBUM_LAUNCHER
echo '#!/bin/sh' > $file
echo '' >> $file
echo "SCRIPT_PATH=\"\$( cd -- \"\$(dirname \"\$0\")\" >/dev/null 2>&1 ; pwd -P )\"" >> $file
echo 'ALBUM_ENV_PATH=$SCRIPT_PATH/env/album' >> $file
echo "$CONDA_EXECUTABLE run --no-capture-output --prefix \$ALBUM_ENV_PATH album \$@" >> $file
chmod +x $ALBUM_LAUNCHER

echo ""
echo ""
echo ""
echo "~~~ Successfully installed album ~~~"
echo ""
echo "Activate and use the album environment like this:"
echo "  source $ALBUM_ACTIVATE"
echo "  album --help"
echo "  album .."
echo "  source $ALBUM_DEACTIVATE"
echo ""
echo "In case conda is printing a long directory prefix once activated, you can call this command to shorten it:"
echo "  $CONDA_EXECUTABLE config --set env_prompt '({name})'"
echo ""
echo ""
echo "Use run-album to run single album commands directly (this is slower when running consecutive album calls than activating the environment first):"
echo ""
echo "  $ALBUM_LAUNCHER --help"
echo ""
echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
echo ""
