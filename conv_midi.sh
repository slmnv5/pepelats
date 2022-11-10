#!/bin/sh
# This script starts MIDI converter mimap5 (github link below)

# Part of hardware MIDI port name - source of messages
HARDWARE_NAME="BlueBoard"

THIS_DIR=$(dirname "$0")
cd "$THIS_DIR" || exit 1

check_running() {
  found=$(pgrep mimap5)
  if [ -n "$found" ]; then
    echo "Exiting, already running"
    exit 0
  fi
}

# wait for MIDI bluetooth to connect
sleep 20

#wget -nc -O mimap5 https://github.com/slmnv5/mimap5/blob/master/mimap5?raw=true
chmod a+x mimap5

while true; do

check_running
# Start using typing keyboard
sudo ./mimap5 -r rules.txt -k kbdmap.txt -n PedalCommands "$@" &
sleep 10

check_running
# Start using MIDI source
./mimap5 -r rules.txt -i $HARDWARE_NAME -n PedalCommands "$@" &
sleep 10

done
