# Pepelats - Software looper on Raspberry Pi.

## Features

- Arbitrary number of song parts (verse/chorus/bridge) each made of any number of parallel loops
- Parallel loops in song part may have different length (number of bars)
- Song parts and loops have "undo/redo" and may be added/deleted on the run
- Drum machine with random patterns and breaks configureable in a text file
- Quantization - time of changing parts, recording is adjusted to keep rhythm intact
- Songs may be saved and loaded from SD card
- MIDI over Bluetooth or USB configureable in a text file
- Text console shows loop position, state, length and volume of each part and loop
- Menu to display, change looper parameters using only foot controller

## Installation:

Install Raspberry Pi OS Lite, LCD screen and drivers. To make text readable on 3.5 inch LCD select font Terminus 16x32
using command: sudo dpkg-reconfigure console-setup

Install dependencies running script [install_dependencies.sh](config/etc/scripts/install_dependencies.sh)

Clone this repository:

- cd ~/; git clone https://github.com/slmnv5/pepelats

To enable auto start edit ~/.bashrc file, append this line:

- $HOME/pepelats/start.sh

# [Pepelats details](./details.md)
