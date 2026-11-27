#!/usr/bin/env bash

os=$(uname -s)
echo "$os"

# Kill any OTHER running loop.sh instances (without killing this script $$)
for pid in $(pgrep -f "loop\.sh"); do
  if [ "$pid" != "$$" ] && [ "$pid" != "$PPID" ]; then
    kill -9 "$pid" 2>/dev/null
  fi
done

pkill -9 main.bin 2>/dev/null
pkill -9 python3 2>/dev/null

mkdir -p ~/save_song
cd "$(dirname "$0")" || exit 1

if [ ! -f ./license.ini ]; then
  echo -e "\n\n owner: myname@mail.com\n\n license: 01-23-45-67-89-ab-cd-ef\n\n" > ./license.ini
fi

if [ ! -f ./user.ini ]; then
  echo -e "\n\n" > ./user.ini
fi

[ -f log.txt ] && cat log.txt >> old.txt && echo "" > log.txt
[ -f old.txt ] && tail -n 1000 old.txt > old.tmp && mv -f old.tmp old.txt


if [[ "$*" == *--debug* ]] && [[ "$os" == Linux* ]]; then
  echo "-------------- Boot errors ----------------" >> log.txt
  journalctl -p err -b >> log.txt
  echo "-------------- MIDI devices found ---------" >> log.txt
  aconnect -l >> log.txt
  echo "-------------- Audio devices found --------" >> log.txt
  aplay -l >> log.txt
  echo "-------------------------------------------" >> log.txt
fi

if [ -f ./main.dist/main.bin ]; then
  RUN_CMD="./main.dist/main.bin $*"
else
  RUN_CMD="python3 ./src/main.py $*"
  PYTHONPATH="$(python3 -m site --user-site):${PYTHONPATH}"
  export PYTHONPATH
fi

LOG="yes"
if [[ "$*" == *--no-log* ]]; then LOG=""; fi


# disable under voltage error on screen
# sudo dmesg -D
stty -echo
[[ "$os" == Linux* ]] && setfont Uni1-VGA32x16 2>/dev/null

while true; do
  echo "=============== $(date)" >> log.txt
  clear
  if [ -n "$LOG" ]; then $RUN_CMD 2>>log.txt; else $RUN_CMD; fi
  sleep 2
  pkill -9 main.bin 2>/dev/null
  pkill -9 python3 2>/dev/null
  sleep 1
done

stty echo
[[ "$os" == Linux* ]] && setfont Uni1-VGA32x16 2>/dev/null
