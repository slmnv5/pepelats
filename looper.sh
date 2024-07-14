#!/bin/sh

test_keyboard() {
  # sudo required for keyboard
  SUDO=""
  HAS_KBD=""
  if lsusb | grep -i "USB Keyboard"; then HAS_KBD="YES"; SUDO="sudo -E"; fi
  export HAS_KBD
}

TMP=$(dirname "$0")
cd "$TMP" || exit 1

if pidof -o %PPID -x "looper.sh">/dev/null; then
    echo "Process already running"
    exit 1
fi

if [ ! -d ".save_song" ]; then mkdir -p ".save_song"; fi
touch local.ini

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

# disable under voltage error on screen, set huge font size, disable typing echo
sudo dmesg -D
sudo setfont Uni1-VGA32x16
stty -echo

while true; do
  killall -9 -qw python > /dev/null
  test_keyboard
  PYTHON_CMD="$SUDO python $CODE_OPTIMIZE ./src/start_looper.py $*"
  echo "$PYTHON_CMD"
  sleep 5
  $PYTHON_CMD
done

sudo dmesg -E
sudo setfont Uni1-VGA16
stty echo
