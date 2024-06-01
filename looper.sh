#!/bin/sh

TMP=$(dirname "$0")
cd "$TMP" || exit 1

found=$(pgrep --full start_looper.py)
if [ -n "$found" ]; then
  echo "Exiting, already running"
  exit 1
fi

sleep 5

if [ ! -d ".save_song" ]; then mkdir -p ".save_song"; fi
touch local.ini

cd "./src" || exit 1

sudo chmod a+rw ./.save_song/*
touch log.txt
chmod a+rw log.txt
cp log.txt log.bak
tail -n 1000 log.bak > log.txt
echo "===========================" >> log.txt
date >> log.txt


# disable assert
CODE_OPTIMIZE="-O"
for var in "$@"; do
  if [ "$var" = "--debug" ] || [ "$var" = "--info" ]; then
    CODE_OPTIMIZE=""
  fi
done

# sudo required for keyboard
SUDO=""
if lsusb | grep -i "USB Keyboard"; then export HAS_KBD="YES"; SUDO="sudo -E"; fi

PYTHON_CMD="$SUDO python $CODE_OPTIMIZE ./start_looper.py $*"
echo "$PYTHON_CMD"

# disable under voltage error on screen, set huge font size, disable typing echo
sudo dmesg -D
sudo setfont Uni1-VGA32x16
stty -echo

while true; do
  killall -s 9 -w -v python
  git reset --hard
  git pull
  $PYTHON_CMD
  sleep 5
done

sudo dmesg -E
sudo setfont Uni1-VGA16
stty echo
