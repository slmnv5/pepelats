#!/bin/sh

TMP=$(dirname "$0")
cd "$TMP" || exit 1
ROOTDIR="$(pwd -P)"
APPDIR=$(basename "$ROOTDIR")
export APPDIR

found=$(pgrep --full start_looper.py)
if [ -n "$found" ]; then
  echo "Exiting, already running"
  exit 1
fi

sleep 5

if [ ! -d "$ROOTDIR/.save_song" ]; then mkdir -p "$ROOTDIR/.save_song"; fi

cd "$ROOTDIR/src" || exit 1

cat "/tmp/log.txt" >> "$ROOTDIR/log.bak"
date > "/tmp/log.txt"

tail -1000 "$ROOTDIR/log.bak" > "$ROOTDIR/tmp"
mv -fv "$ROOTDIR/tmp" "$ROOTDIR/log.bak"


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

# disable under voltage error on screen, set huge font size, disable typing echo
sudo dmesg -D
sudo setfont Uni1-VGA32x16
stty -echo

while true; do
  killall -s 9 -w -v python
  $PYTHON_CMD
  sleep 5
done

sudo dmesg -E
sudo setfont Uni1-VGA16
stty echo
