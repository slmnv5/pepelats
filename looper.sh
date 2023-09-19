#!/bin/sh

TMP=$(dirname "$0")
cd "$TMP" || exit 1
RDIR="$(pwd -P)"
mkdir "$RDIR/save_song"
cd "$RDIR/src" || exit 1

found=$(pgrep --full start_looper.py)
if [ -n "$found" ]; then
  echo "Exiting, already running"
  exit 1
fi

sleep 5

cat "$RDIR/log.txt" >> "$RDIR/log.bak"
date > "$RDIR/log.txt"

# disable assert
CODE_OPTIMIZE="-O"
# use sudo and computer keyboard
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
  if [ -f $RDIR/connect_bt.sh ]; then $RDIR/connect_bt.sh; fi
  $PYTHON_CMD
  sleep 5
done

sudo dmesg -E
stty echo
