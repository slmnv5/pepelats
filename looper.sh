#!/bin/sh

TMP=$(dirname "$0")
cd "$TMP"
export ENV_ROOT_DIR="$(pwd -P)"
cd "$ENV_ROOT_DIR/src" || exit 1

CONFIG_FILE="$ENV_ROOT_DIR/.saved_env.sh"
touch "$CONFIG_FILE"
. "$CONFIG_FILE"


found=$(pgrep --full start_looper.py)
if [ -n "$found" ]; then
  echo "Exiting, already running"
  exit 1
fi

CODE_OPTIMIZE="-O"
SUDO=""
for var in "$@"; do
  if [ "$var" = "--debug" ] || [ "$var" = "--info" ]; then
    CODE_OPTIMIZE=""
  fi
  if [ "$var" = "--kbd" ]; then
    SUDO="sudo"
  fi
done

PYTHON_CMD="$SUDO python $CODE_OPTIMIZE ./start_looper.py  $*"
echo "$PYTHON_CMD"

# disable under voltage error on screen and disable typing echo
sudo dmesg -D
stty -echo

while true; do
  killall -s 9 -w -v python
  . "$CONFIG_FILE"
  sleep 2
  $PYTHON_CMD
done

sudo dmesg -E
stty echo
