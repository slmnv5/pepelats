#!/bin/bash

if pidof -o %PPID -x loop.sh > /dev/null; then
    echo "Process already running"
    exit 1
fi

cd "$(dirname "$0")" || exit 1

SAVE_SONG=~/save_song
LOG=log.txt
BAK=log.bak

# delete later
mv -v loop.ini local.ini 2>/dev/null

mkdir "$SAVE_SONG" 2>/dev/null
touch "$LOG"
cat "$LOG" >> "$BAK"
chmod a+rw "$SAVE_SONG/*" 2>/dev/null
tail -n 1000 "$BAK" > "$LOG"
mv "$LOG" "$BAK"
echo "== $(date) ==" > "$LOG"

if [ ! -f "./local.ini" ]; then
  cp -pnv main.ini local.ini
fi

# sudo required for keyboard input
SUDO=""
for var in "$@"; do
  if [ "$var" == "--kbd" ]; then
    SUDO="sudo -E"
  fi
done


KILL_CMD="$SUDO pkill -9 main.bin"
RUN_CMD="$SUDO ./main.dist/main.bin $*"
if [ ! -f ./main.dist/main.bin ]; then
  KILL_CMD="$SUDO pkill -9 python"
  RUN_CMD="$SUDO python ./src/main.py $*"
fi

export HAS_FB=""
if [ -e /dev/fb[0-5] ]; then HAS_FB="1"; fi


# disable under voltage error on screen, disable typing echo
sudo dmesg -D
stty -echo
sudo setfont Uni1-VGA32x16
while true; do
  $KILL_CMD
  sleep 3
  echo "===== $RUN_CMD ====="
  $RUN_CMD
  if [ "$?" != "0" ]; then sleep 50; fi
done
sudo dmesg -E
stty echo
sudo setfont Uni1-VGA16

