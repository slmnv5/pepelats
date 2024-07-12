## Installation

*1) Install latest Raspberry Pi OS Lite (bookworm as of today).

*2) Install dependencies and LCD screen with driver running
script [install_dependencies.sh](etc/scripts/install_dependencies.sh)

*3) Clone this repository:

```
cd ~/; git clone https://github.com/slmnv5/pepelats
```

*4) To enable auto start edit ~/.bashrc file, append this line:

```
$HOME/pepelats/looper.sh
```

*5) Connect MIDI controller and make sure it's name (or part of name) is listed in main.ini [MIDI] section and the
notes it sends are listed there as well.

If controller is not found and computer keyboard is connected it will be used for control. Keys are configured in
main.ini. On Windows keys are fixed: '1,2,3,4,q,w' and used just for testing.

### Command line parameters

Below parameters are used for troubleshooting

- --info -- verbose logging
- --debug -- more verbose logging
- --keep_screen -- keep logging output on screen to see errors

log.txt -- is the log file that keeps about 1000 latest lines of all session.
