## Installation

*1) Install latest Raspberry Pi OS Lite (bookworm as of today).

*2) Clone this repository and install LCD screen driver running script:  
[install_lcd.sh](./../config/etc/scripts/install_lcd.sh)

*3) To enable auto start edit ~/.bashrc file, append this line:

```
$HOME/pepelats/looper.sh
```

*4) Connect MIDI controller and make sure it's name (or part of name) is listed in local.ini [MIDI] section.
For an example look at main.ini file. If MIDI controller is missing computer keyboard will be used.

*5) To check MIDI notes (keyboard keys) the looper is using look at menu configuration
in [config.ini](./../config/menu/6-4-menu/config.ini)  
The MIDI notes (keyboard keys) are listed in [MIDI] section.

If MIDI controller is not found and computer keyboard is connected it will be used for control. Keys are configured in
main.ini file.
On Windows keys are fixed: '1,2,3,4,q,w'.

### Command line parameters

Below parameters are used for troubleshooting

- --info -- verbose logging
- --debug -- more verbose logging

log.txt -- is the log file for the latest session.
log.bak -- keeps about 1000 lines from the past.
