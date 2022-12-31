#!/bin/sh
# This script starts pepelats audio looper
# Options are:
# --debug or --info - level of logging
# --kbd - use keyboard for MIDI input (see KBD_NOTES)
# --count - count notes


TMP=$(dirname "$0")
cd "$TMP"
export ENV_ROOT_DIR="$(pwd -P)"
cd "$ENV_ROOT_DIR/src" || exit 1
CONFIG_FILE="$ENV_ROOT_DIR/.saved_env.sh"
touch "$CONFIG_FILE"
. "$CONFIG_FILE"
env



#killall -9 python
export PYTHONPATH="${PYTHONPATH}:$HOME/mypi_music/src:$HOME/mypi_music"

python ./drum/_mididrum.py

