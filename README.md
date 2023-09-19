# Pepelats - Audio looper

## Features

- Multiple song parts (verse/chorus/bridge)
- Parallel loops of variable length: 0.25, 0.5, 1, 2, 3 ... of initial loop
- Full history for "undo/redo", not only the latest change
- Loops and parts added/deleted on the run
- Quantization - time of changing parts, recording is adjusted
- Drum machine with 3 drum types: Pattern drum, MIDI drum and Loop drum. MIDI drum can sync and control external MIDI
  drum machine, Pattern drum supports randomization and Loop drum is just an audio loop always playing
- Songs saved and loaded from SD card
- Control of looper by MIDI (Bluetooth or USB) or by computer keyboard
- Optional graphics mode with LCD touch screen menu

## Installation:

Install Raspberry Pi OS Lite, LCD screen with driver.
To make text readable on 3.5 inch LCD select font Terminus 16x32
using command: sudo dpkg-reconfigure console-setup

Install dependencies running script [install_dependencies.sh](config/etc/scripts/install_dependencies.sh)
Clone repository:

- cd ~/; git clone https://github.com/slmnv5/pepelats

To enable auto start edit ~/.bashrc file, append this line:

- $HOME/pepelats/looper.sh

# [Read more details](details.md)
