#!/bin/bash

if pidof -o %PPID -x loop.sh > /dev/null; then
    echo Process already running
    exit 1
fi

cd "$(dirname "$0")" || exit 1

SAVE_SONG=~/save_song
LOG=./log.txt
OLD=./old.txt
SRT=./start.txt
USR=./user.ini
LIC=./license.ini

mkdir "$SAVE_SONG" 2>/dev/null
chmod a+rw "$SAVE_SONG/*" 2>/dev/null

if [ ! -f "$LIC" ]; then
  printf "\n\nowner: myname@mail.com\n\nlicense: 9c-9b-f1-20-39-45-de-40\n\n" > "$LIC"
fi

touch "$LOG" "$USR"
cat "$LOG" >> "$OLD"
tail -n 1000 "$OLD" > "$LOG"
mv "$LOG" "$OLD"
echo "" > "$LOG"


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

echo "" > $SRT

if [[ "$*" == *"--web"* ]]; then
  echo "export LOOP_USE_WEB=1" >> $SRT
fi

if [[ "$*" == *"--lcd"* ]]; then
  echo "export LOOP_USE_LCD=1" >> $SRT
fi

if [ -e /dev/fb0 ] || [ -e /dev/fb1 ] || [ -e /dev/fb2 ]; then
  echo "export LOOP_HAS_FB=1" >> $SRT
fi

# disable under voltage error on screen, disable typing echo
sudo dmesg -D
stty -echo
sudo setfont Uni1-VGA32x16
while true; do
  source ./start.txt
  echo "===== $LOOP_RUN_CMD" >> $LOG
  echo "===== $(date)" >> $LOG
  clear
  $LOOP_RUN_CMD 2>>$LOG
  sleep 5
  $LOOP_KILL_CMD 2>/dev/null
done
sudo dmesg -E
stty echo
sudo setfont Uni1-VGA16

