#!/bin/sh

# sudo required for keyboard
SUDO=""

 if pidof -o %PPID -x "$(basename "$0")">/dev/null; then
    echo "Process already running"
    exit 1
fi
cd "$(dirname "$0")" || exit 1

mkdir ~/save_song 2>/dev/null
touch local.ini log.txt log.bak
chmod a+rw log.txt log.bak ~/save_song/* 2>/dev/null
cat log.txt >> log.bak
tail -n 1000 log.bak > log.txt
mv log.txt log.bak
echo "== $(date) ==" > log.txt

for var in "$@"; do
  if [ "$var" = "--kbd" ] || [ "$var" = "--keyboard" ]; then
    SUDO="sudo -E"
  fi
done

# disable under voltage error on screen, set huge font size, disable typing echo
sudo dmesg -D
sudo setfont Uni1-VGA32x16
#stty -echo
for count in 1 2 3 4 5 6 7 8 9; do
  echo "run # $count"
  killall -9 -qw python > /dev/null
  PYTHON_CMD="$SUDO ./main.dist/main.bin $*"
  $PYTHON_CMD
  if [ "$?" -ne "0" ]; then sleep 10; fi
done

#sudo dmesg -E
sudo setfont Uni1-VGA16
#stty echo

