#!/bin/bash

if pidof -o %PPID -x loop.sh > /dev/null; then
    echo Process already running
    exit 1
fi

cd "$(dirname "$0")" || exit 1

SAVE_SONG=~/save_song
LOG=./log.txt
OLD=./old.txt
USR=./user.ini
LIC=./license.ini

mkdir "$SAVE_SONG" 2>/dev/null
chmod a+rw "$SAVE_SONG/*" 2>/dev/null

if [ ! -f "$LIC" ]; then
  echo -e "\n\n owner: myname@mail.com\n\n license: 9c-9b-f1-20-39-45-de-40\n\n" > "$LIC"
fi

touch "$LOG" "$USR"
cat "$LOG" >> "$OLD"
tail -n 1000 "$OLD" > "$LOG"
mv "$LOG" "$OLD"
echo "" > "$LOG"

#====== save start options in start.txt
echo "" > ./start.txt
USE_SUDO=""
if [[ "$*" == *"--kbd"* ]]; then
  USE_SUDO="sudo -E"
fi
if [[ "$*" == *"--web"* ]]; then
  echo "export USE_WEB=1" > ./start.txt
fi
if [[ "$*" == *"--lcd"* ]]; then
  echo "export USE_LCD=1" > ./start.txt
fi
if [ ! -f ./main.dist/main.bin ]; then
  export KILL_CMD="$USE_SUDO pkill -9 python"
  export RUN_CMD="$USE_SUDO python ./src/main.py $*"
else
  export KILL_CMD="$USE_SUDO pkill -9 main.bin"
  export RUN_CMD="$USE_SUDO ./main.dist/main.bin $*"
fi

function kill_conn {
  while true; do
    conn=$(sudo fuser -n tcp -v 8000)
    echo "$conn ======> " >> "$LOG"
    sudo netstat -pnat | grep 8000 >> "$LOG"
    if [ -z "$conn" ]; then return; fi
    sudo fuser -k  8000/tcp
    sleep 2
  done
}
# disable under voltage error on screen, disable typing echo
sudo dmesg -D
stty -echo
sudo setfont Uni1-VGA32x16
while true; do
  source ./start.txt
  echo "===== $RUN_CMD" >> $LOG
  echo "===== $(date)" >> $LOG
  clear
  $RUN_CMD 2>>$LOG
  #kill_conn

  sleep 5
  $KILL_CMD 2>/dev/null
done
sudo dmesg -E
stty echo
sudo setfont Uni1-VGA16

