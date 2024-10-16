#!/bin/sh

  # sudo required for keyboard
  SUDO=""
  export HAS_KBD=""

test_all() {
  # sudo required for keyboard
  SUDO=""
  HAS_KBD=""
  if lsusb | grep -i "USB Keyboard"; then HAS_KBD="YES"; SUDO="sudo -E"; fi
}

TMP=$(dirname "$0")
cd "$TMP" || exit 1

if pidof -o %PPID -x "looper.sh">/dev/null; then
    echo "Process already running"
    exit 1
fi

sudo chmod a+rw ./save_song/*
touch local.ini log.txt
chmod a+rw log.txt log.bak
cat log.txt >> log.bak
tail -n 1000 log.bak > log.txt
mv log.txt log.bak
echo "== $(date) ==" > log.txt

# disable under voltage error on screen, set huge font size, disable typing echo
sudo dmesg -D
sudo setfont Uni1-VGA32x16
stty -echo
while true; do
  test_all
  killall -9 -qw python > /dev/null
  PYTHON_CMD="$SUDO ./main.dist/main.bin $*"
  clear
  $PYTHON_CMD
  if [ "$?" -ne "0" ]; then sleep 30; fi
done

sudo dmesg -E
sudo setfont Uni1-VGA16
stty echo
