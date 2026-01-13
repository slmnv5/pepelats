#!/bin/bash

if pidof -o %PPID -x loop.sh > /dev/null; then
    echo Process already running
    exit 1
fi

mkdir ~/save_song
sudo chmod a+rw ~/save_song/*

cd "$(dirname "$0")" || exit 1

if [ ! -f ./license.ini ]; then
  echo -e "\n\n owner: myname@mail.com\n\n license: 9c-9b-f1-20-39-45-de-40\n\n" > ./license.ini
fi

if [ ! -f ./user.ini ]; then
  cp -v ./main.ini ./user.ini
fi

LOG=./log.txt

cat "$LOG" >> ./old.txt
tail -n 1000 ./old.txt > ./tmp.txt
mv ./tmp.txt ./old.txt
echo "======= $(date) =======" > $LOG

# sudo required for keyboard input
SUDO=""
if [[ "$*" == *"--kbd"* ]]; then
  SUDO="sudo -E"
fi

if [ ! -f ./main.dist/main.bin ]; then
  export KILL_CMD="$SUDO pkill -9 python"
  export RUN_CMD="$SUDO python ./src/main.py"
else
  export KILL_CMD="$SUDO pkill -9 main.bin"
  export RUN_CMD="$SUDO ./main.dist/main.bin"
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
  echo "=== $RUN_CMD" >> $LOG
  clear
  $RUN_CMD 2>>$LOG
  #kill_conn

  sleep 5
  $KILL_CMD 2>/dev/null
done
sudo dmesg -E
stty echo
sudo setfont Uni1-VGA16

