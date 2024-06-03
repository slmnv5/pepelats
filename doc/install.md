## Installation

*1) Install latest Raspberry Pi OS Lite (bookworm as of today).

*2) Install dependencies and LCD screen with driver running
script [install_dependencies.sh](./../config/etc/scripts/install_dependencies.sh)

*3) Clone this repository:

```
cd ~/; git clone https://github.com/slmnv5/pepelats
```

*4) To enable auto start edit ~/.bashrc file, append this line:

```
$HOME/pepelats/looper.sh
```

*5) If computer keyboard is cobnnected it will be used for control. Keys and MIDI notes are configured in **main.ini**.

Alternatively connect MIDI controller and make sure it's name (or part of name) is listed in **main.ini** [MIDI] section

### Command line parameters

Below parameters are used for troubleshooting

- --info -- verbose logging
- --debug -- more verbose logging
- --keep_screen -- keep logging output on screen to see errors

log.txt -- is the log file that keeps about 1000 latest lines of all session session.
