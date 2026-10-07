#!/bin/bash

if pidof -o %PPID -x loop.sh > /dev/null; then
  echo Process already running
  exit 1
fi

mkdir -p ~/save_song

cd "$(dirname "$0")" || exit 1

if [ ! -f ./license.ini ]; then
  echo -e "\n\n owner: myname@mail.com\n\n license: 01-23-45-67-89-ab-cd-ef\n\n" > ./license.ini
fi

if [ ! -f ./user.ini ]; then
  echo -e "\n\n" > ./user.ini
fi


cat log.txt >> old.txt
tail -n 1000 old.txt > log.txt
mv -f log.txt old.txt
echo "-------------- boot errors ----------------" > log.txt
journalctl -p err -b >> log.txt
echo "-------------------------------------------" >> log.txt

if [ -f ./main.dist/main.bin ]; then
  export KILL_CMD="pkill -9 main.bin"
  export RUN_CMD="./main.dist/main.bin"
else
  export KILL_CMD="pkill -9 python3"
  export RUN_CMD="python3 ./src/main.py $*"
  PYTHONPATH="$(python3 -m site --user-site):${PYTHONPATH}"
  export PYTHONPATH
fi


# disable under voltage error on screen
# sudo dmesg -D
stty -echo
setfont Uni1-VGA32x16
while true; do
  echo "=============== $(date)" >> log.txt
  clear
  $RUN_CMD 2>>log.txt 
  sleep 5
  $KILL_CMD 2>/dev/null
done
stty echo
setfont Uni1-VGA16
