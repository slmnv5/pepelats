#!/bin/bash

if pidof -o %PPID -x loop.sh > /dev/null; then
    echo "Process already running"
    exit 1
fi

cd "$(dirname "$0")" || exit 1

SAVE_SONG=~/save_song
LOG=log.txt
BAK=log.bak

mv -v loop.ini local.ini

mkdir "$SAVE_SONG" 2>/dev/null
touch "$LOG"
cat "$LOG" >> "$BAK"
chmod a+rw "$SAVE_SONG/*" 2>/dev/null
tail -n 1000 "$BAK" > "$LOG"
mv "$LOG" "$BAK"
echo "== $(date) ==" > "$LOG"

if [ ! -f "./local.ini" ]; then
  copy -pnv main.ini local.ini
fi


# sudo required for keyboard input
SUDO=""
OPTIMIZE="-O"
for var in "$@"; do
  if [ "$var" == "--kbd" ]; then
    SUDO="sudo -E"
  fi
  if [ "$var" == "--info" ] || [ "$var" == "--debug" ]; then
    OPTIMIZE=""
  fi
done


KILL_CMD="$SUDO pkill -9 main.bin"
RUN_CMD="$SUDO ./main.dist/main.bin $*"
if [ ! -f ./main.dist/main.bin ]; then
  KILL_CMD="$SUDO pkill -9 python"
  RUN_CMD="$SUDO python $OPTIMIZE ./src/main.py $*"
fi


# disable under voltage error on screen, disable typing echo
sudo dmesg -D
stty -echo
sudo setfont Uni1-VGA32x16
while true; do
  $KILL_CMD
  sleep 3
  echo "===== $RUN_CMD ====="
  $RUN_CMD
done
sudo dmesg -E
stty echo
sudo setfont Uni1-VGA16

