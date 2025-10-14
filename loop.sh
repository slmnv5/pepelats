#!/bin/bash

if pidof -o %PPID -x loop.sh > /dev/null; then
    echo Process already running
    exit 1
fi

cd "$(dirname "$0")" || exit 1

SAVE_SONG=~/save_song
LOG=./log.txt
OLD=./old.txt
START=./start.txt
INI=./local.ini

mkdir "$SAVE_SONG" 2>/dev/null
chmod a+rw "$SAVE_SONG/*" 2>/dev/null

touch license.ini
touch "$LOG" "$INI"
cat "$LOG" >> "$OLD"
tail -n 1000 "$OLD" > "$LOG"
mv "$LOG" "$OLD"
echo "===== $(date)" > "$LOG"

tmp=$(stat -c %s "$INI")
if [ "$tmp" -le "5" ]; then
  cp -pv main.ini local.ini
fi

# order of 2 IFs is important
LOOP_SUDO=""
if [[ "$*" == *"--kbd"* ]]; then
  LOOP_SUDO="sudo -E"
fi

if [ ! -f ./main.dist/main.bin ]; then
  export LOOP_KILL_CMD="$LOOP_SUDO pkill -9 python"
  export LOOP_RUN_CMD="$LOOP_SUDO python ./src/main.py"
else
  export LOOP_KILL_CMD="$LOOP_SUDO pkill -9 main.bin"
  export LOOP_RUN_CMD="$LOOP_SUDO ./main.dist/main.bin"
fi

echo "" > $START

if [[ "$*" == *"--web"* ]]; then
  echo "export LOOP_USE_WEB=1" >> $START
fi

if [ -e /dev/fb0 ] || [ -e /dev/fb1 ] || [ -e /dev/fb2 ]; then
  echo "export LOOP_HAS_FB=1" >> $START
fi

# disable under voltage error on screen, disable typing echo
sudo dmesg -D
stty -echo
sudo setfont Uni1-VGA32x16
while true; do
  # shellcheck disable=SC1090
  source $START
  echo "===== $LOOP_RUN_CMD" >> $LOG
  $LOOP_RUN_CMD 2>>$LOG
  sleep 10
  $LOOP_KILL_CMD 2>/dev/null
done
sudo dmesg -E
stty echo
sudo setfont Uni1-VGA16

