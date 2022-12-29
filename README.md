# Pepelats - Software looper on Raspberry Pi.

## Features

- Any number of song parts (verse/chorus/bridge) each made of parallel loops
- Parallel loops in part may have different length, multiple of a bar
- Full history for "undo/redo", not only the latest change
- Loops, parts may be added/deleted on the run
- Drum machine with random patterns/breaks configureable in a text file
- Quantization - time of changing parts, recording is adjusted to keep the rhythm
- Songs saved and loaded from SD card
- Control by MIDI (Bluetooth / USB) configureable in a text file
- Typing keyboard may be used as MIDI controller
- Text console shows loop position, state, length, volume
- MIDI control supplemented by LCD touch screen menu
- Drums sent to MIDI OUT port instead of playing internal samples

## Installation:

Install Raspberry Pi OS Lite, LCD screen and drivers. To make text readable on 3.5 inch LCD select font Terminus 16x32
using command: sudo dpkg-reconfigure console-setup

Install dependencies running script [install_dependencies.sh](etc/scripts/install_dependencies.sh)
Clone this repository:

- cd ~/; git clone https://github.com/slmnv5/pepelats

To enable auto start edit ~/.bashrc file, append this line:

- $HOME/pepelats/looper.sh

# [Read more details](details.md)
